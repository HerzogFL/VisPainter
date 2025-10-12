import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple

import fitz                         
from PIL import Image, ImageDraw
import cv2
from openai import AzureOpenAI
import pikepdf
from pikepdf import Dictionary, Array


AZURE_ENDPOINT   = ""
AZURE_API_KEY    = ""
AZURE_API_VERSION= ""
AZURE_MODEL_NAME = ""

STEP_PAT = re.compile(r"_step_(\d+)", re.IGNORECASE)

def extract_step_number(pdf_name: str) -> int:

    m = STEP_PAT.search(pdf_name)
    return int(m.group(1)) if m else 0

def ensure_out_dir(out_dir: Path):

    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)

def normalize_tokens(txt: str) -> List[str]:

    if '"label"' in txt:                                    
        raw_labels = re.findall(r'"label"\s*:\s*"([^"]+)"', txt)
    else:                                                  
        raw_labels = [line.strip() for line in txt.splitlines() if line.strip()]


    norm_labels: List[str] = []
    for lab in raw_labels:
        lab_low = lab.lower()


        lab_low = re.sub(r"[\s\.,;:!?\-—_·`'\"“”‘’]", "", lab_low)

        lab_low = re.sub(r"[()\[\]{}<>（）【】]", "", lab_low)


        lab_low = re.sub(r"[^0-9a-z\+]+", "", lab_low)

        if lab_low:                                         
            norm_labels.append(lab_low)

    return norm_labels


def counter_overlap(tokens_a: List[str], tokens_b: List[str]) -> Tuple[float, float]:

    if not tokens_a or not tokens_b:
        return 0.0, 0.0
    cnt_a, cnt_b = Counter(tokens_a), Counter(tokens_b)
    common = (cnt_a & cnt_b).total()
    precision = common / len(tokens_a)
    recall    = common / len(tokens_b)
    return precision, recall

def inverse_ratio(val: float, max_fail: float = 1.0) -> float:

    return 1.0 / (1.0 + 2*val / max_fail)

def encode_image_b64(img_path: Path) -> str:

    return base64.b64encode(img_path.read_bytes()).decode()


def pdf_extract_text(pdf_path: Path, save_dir: Path) -> Tuple[str, Path]:

    collected: List[str] = []

    reg_page  = re.compile(r"^页\s*-\s*\d+$")
    reg_sheet = re.compile(r"^sheet\.\d+$", re.I)

    def _walk(node):
        if not isinstance(node, Dictionary):
            return

        if "/K" in node:
            kids = node.K
            if isinstance(kids, Array):
                for kid in kids:
                    _walk(kid)
            else:
                _walk(kids)

        txt_value = None
        if "/A" in node and "/ActualText" in node.A:
            txt_value = str(node.A["/ActualText"])
        elif "/Alt" in node:
            txt_value = str(node.Alt)

        if not txt_value:
            return

        txt_value = txt_value.strip()
        if (not txt_value or reg_page.match(txt_value) or reg_sheet.match(txt_value)):
            return

        collected.append(txt_value)


    with pikepdf.open(pdf_path) as pdf:
        if "/StructTreeRoot" in pdf.Root:
            _walk(pdf.Root.StructTreeRoot)


    json_path = save_dir / f"{pdf_path.stem}_pdf_labels.json"
    text_json = [{"label": t} for t in collected]
    json_path.write_text(json.dumps(text_json, ensure_ascii=False, indent=2), "utf-8")

    return "\n".join(collected), json_path

def pdf_render_first_page(pdf_path: Path, save_dir: Path, dpi: int = 200) -> Path:

    png_path = save_dir / f"{pdf_path.stem}.png"
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    with fitz.open(pdf_path) as doc:
        pix = doc.load_page(0).get_pixmap(matrix=matrix, alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        img.save(png_path)
    return png_path

def add_grid_to_png(png_path: Path, save_dir: Path, grid_size: int = 128) -> Path:

    img = Image.open(png_path).convert("RGB")
    w, h = img.size
    draw = ImageDraw.Draw(img)
    for x in range(0, w, grid_size):
        draw.line([(x, 0), (x, h)], fill=(0, 0, 0), width=1)
    for y in range(0, h, grid_size):
        draw.line([(0, y), (w, y)], fill=(0, 0, 0), width=1)
    grid_png = save_dir / f"{png_path.stem}_grid.png"
    img.save(grid_png)
    return grid_png


def alignment_score(png_path: Path) -> float:

    img = cv2.imread(str(png_path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    horizontal_projection = gray.mean(axis=1)
    var_value = float(horizontal_projection.var())
    score = 1.0 / (1.0 + var_value / 1e4)   
    return score

def gpt_design_errors(png_path: Path) -> Tuple[int, str]:

    prompt =(
            f"You need to observe this picture carefully. This is a scientific research drawing. How many unreasonable aspects do you think there are in this image?"
            f"Unreasonable aspects refer to: position conflicts or mismatches of modules; text content and module size conflicts resulting in text going out of range or unexpected line breaks; redundant or repetitive designs in the image."
            f"For each unreasonable aspect you find, you need to provide some analysis, in the format like: Module 1: The position conflicts with Module 2, causing overlap..."
            f"When finding problems, you must be strict and try to find as many design errors as possible. But at the same time, each problem must be well - founded."
            f"At the end, you need to output only one number representing the number of errors. Make a line break from the previous content. Write only one integer on a separate line at the end to represent the total number of errors."
    )
    client = AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        api_version=AZURE_API_VERSION,
    )
    b64 = encode_image_b64(png_path)
    response = client.chat.completions.create(
        model=AZURE_MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text",      "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
            }
        ]
    )
    content = response.choices[0].message.content

    match = re.search(r"(\d+)\s*$", content)
    if not match:
        raise RuntimeError("GPT did not return the number of errors. Original text: \n" + content)
    num_errors = int(match.group(1))
    analysis   = content.rsplit("\n", 1)[0]  
    return num_errors, analysis

def gpt_blank_ratio(grid_png: Path, grid_size: int = 128) -> float:

    prompt =(
        f"This is a scientific research drawing. A black grid with a size of {grid_size} pixels has been added to the drawing."
        f"Please estimate the proportion of the large - area blank space (not the blank space at the edges) inside the image to the entire image based on the grid."
        f"Express it as a number between 0 and 1 and keep only two decimal places. If the blank space in the image makes the picture look harmonious,"
        f"it is not considered as wrong blank space. You only need to estimate the area of the wrong blank space that makes the picture look worse."
        f"Finally, only output the number without any unit or explanation."
    )
    client = AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        api_version=AZURE_API_VERSION,
    )
    b64 = encode_image_b64(grid_png)
    rsp = client.chat.completions.create(
        model=AZURE_MODEL_NAME,
        messages=[{
            "role": "user",
            "content": [
                {"type":"text", "text": prompt},
                {"type":"image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]
        }]
    )
    content = rsp.choices[0].message.content.strip()
    m = re.search(r"[-+]?\d*\.?\d+", content)
    if not m:
        raise RuntimeError("Unable to parse the white space ratio returned by GPT: \n" + content)
    return float(m.group(0))

READ_PROMPT = (
    f"Please list all the text elements that appear in this scientific research drawing (including module titles, annotations, formulas, etc.)."
    f"When searching, it needs to be carried out strictly. If the text is occluded, overlapped, or a word has an unexpected line break, it is not considered readable."
    f"Finally, directly output a JSON array, where each element is a string, for example:"
    f'["Input","Weight layer","ReLU"].'
    f"Do not output any additional explanations, annotations, or key names."
)

def gpt_extract_labels(png_path: Path, save_dir: Path) -> Tuple[List[str], Path]:

    client = AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        api_version=AZURE_API_VERSION,
    )
    b64 = encode_image_b64(png_path)
    messages = [{
        "role":"user",
        "content":[
            {"type":"text", "text": READ_PROMPT},
            {"type":"image_url",
             "image_url":{"url": f"data:image/jpeg;base64,{b64}"}}
        ]
    }]
    content = ""

    for _ in range(3):
        rsp = client.chat.completions.create(model=AZURE_MODEL_NAME, messages=messages)
        content = rsp.choices[0].message.content.strip()
        m = re.search(r"\[.*\]", content, re.S)
        try:
            labels_json = json.loads(m.group(0) if m else content)
            if isinstance(labels_json, list):
                labels = [str(x).strip() for x in labels_json if str(x).strip()]
                break
        except json.JSONDecodeError:
            messages.append({"role":"system","content":"Only output a pure JSON array!"})
    else:
        raise RuntimeError("The GPT response cannot be parsed into an array: \n" + content)

    out_json_path = save_dir / f"{png_path.stem}_pdf_labels_readability.json"
    out_json_path.write_text(json.dumps([{"label": l} for l in labels],
                                        ensure_ascii=False, indent=2), "utf-8")
    return labels, out_json_path

def readability_precision(pred_labels: List[str],
                          ref_labels:  List[str]) -> Tuple[float, List[str], List[str]]:

    pred_tokens = normalize_tokens("\n".join(pred_labels))
    ref_tokens  = normalize_tokens("\n".join(ref_labels))

    if not pred_tokens:
        return 0.0, pred_tokens, ref_tokens

    common = (Counter(pred_tokens) & Counter(ref_tokens)).total()
    precision = common / len(ref_tokens)
    return precision, pred_tokens, ref_tokens

def adjust_with_steps(score_pre: float, steps: int,
                      K: float = 50.0, bonus_ratio: float = 0.08) -> float:

    sat      = steps / (steps + K)                    
    penalty  = (1.0 - score_pre) * sat
    score_p  = score_pre * (1.0 - penalty)

    bonus    = bonus_ratio * score_pre * (1.0 - sat) 
    final    = max(0.0, min(1.0, score_p + bonus))
    return final

def evaluate_single_pdf(pdf_path: Path, gt_prompt_path: Path, out_dir: Path) -> Path:

    ensure_out_dir(out_dir)

    gt_prompt = json.loads(gt_prompt_path.read_text("utf-8"))
    
    step_number = extract_step_number(pdf_path.name)   
    pdf_text, text_json_path = pdf_extract_text(pdf_path, out_dir)

    pdf_labels_raw = [obj["label"] for obj in json.loads(text_json_path.read_text())]
    gt_labels_raw  = [obj["label"] for obj in gt_prompt]

    pdf_tokens = normalize_tokens("\n".join(pdf_labels_raw))    
    gt_tokens  = normalize_tokens("\n".join(gt_labels_raw))     

    precision_text, recall_text = counter_overlap(pdf_tokens, gt_tokens)

    png_path = pdf_render_first_page(pdf_path, out_dir)


    err_count, err_analysis = gpt_design_errors(png_path)
    design_score = inverse_ratio(err_count / max(len(gt_prompt), 1))


    grid_png = add_grid_to_png(png_path, out_dir)
    blank_ratio = gpt_blank_ratio(grid_png)
    blank_score = inverse_ratio(blank_ratio)


    gpt_labels, gpt_json_path = gpt_extract_labels(png_path, out_dir)


    readability_score, read_pred_norm, read_ref_norm = readability_precision(gpt_labels, pdf_labels_raw)


    align_score = alignment_score(grid_png)

    weight_table = {
        "precision": 0.2,
        "recall":    0.2,
        "design":    0.2,
        "blank":     0.05,
        "read":      0.25,  
        "align":     0.1,
    }
    final_raw = (
        precision_text * weight_table["precision"] +
        recall_text    * weight_table["recall"]    +
        design_score   * weight_table["design"]    +
        blank_score    * weight_table["blank"]     +
        readability_score * weight_table["read"]    +
        align_score    * weight_table["align"]
    )

    final_score = adjust_with_steps(final_raw, step_number)

    result_dict = {
        "file": pdf_path.name,
        "precision":   round(precision_text, 4),
        "recall":      round(recall_text, 4),
        "design_errs": err_count,
        "design_score":round(design_score, 4),
        "blank_ratio": round(blank_ratio, 4),
        "blank_score": round(blank_score, 4),
        "readability": round(readability_score, 4),
        "align":       round(align_score, 4),
        "step":  step_number,
        "final_raw":   round(final_raw, 4),
        "final":       round(final_score, 4),

        "text_json": str(text_json_path.name),
        "png":       str(png_path.name),
        "grid_png":  str(grid_png.name),
        "gpt_json":  str(gpt_json_path.name),

        "design_analysis": err_analysis,

        "pdf_norm": pdf_tokens,  
        "read_norm": read_pred_norm,     
        "gt_norm":  gt_tokens   
    }

    score_json_path = out_dir / f"{pdf_path.stem}_score.json"
    score_json_path.write_text(json.dumps(result_dict,
                                          ensure_ascii=False, indent=2), "utf-8")
    return score_json_path

def main_single_cli():
    parser = argparse.ArgumentParser(
        description="Single PDF scientific research drawing evaluation (Automatically generate all intermediate files and output the final score.json)）"
    )
    parser.add_argument("pdf",          help="PDF file to be evaluated")
    parser.add_argument("gt_prompt",    help="GT prompt json file")
    parser.add_argument("--outdir",     default="eval_output",
                        help="Output directory for intermediate files and score.json")
    args = parser.parse_args()

    pdf_path       = Path(args.pdf).expanduser().resolve()
    gt_prompt_path = Path(args.gt_prompt).expanduser().resolve()
    out_dir        = Path(args.outdir).expanduser().resolve()

    if not pdf_path.exists():
        sys.exit(f"NO PDF : {pdf_path}")
    if not gt_prompt_path.exists():
        sys.exit(f"NO GT prompt: {gt_prompt_path}")

    score_json = evaluate_single_pdf(pdf_path, gt_prompt_path, out_dir)

    print("\n================== Evaluation completed ==================")
    print(score_json.read_text("utf-8"))
    print(f"\nEvaluation completed {out_dir}")



FILE_PAT = re.compile(r"^(t(?:i)?2i_\d+)_([^_]+?)_step_\d+(?:_[^_]+)*\.pdf$", re.I)

def parse_pdf_filename(pdf_name: str) -> Tuple[str, str]:

    m = FILE_PAT.match(pdf_name)
    if not m:
        raise ValueError(f"Unable to parse pdf file name: {pdf_name}")
    return m.group(1), m.group(2)

def evaluate_batch(pdf_dir: Path,
                   gt_dir:  Path,
                   out_dir: Path) -> Path:

    ensure_out_dir(out_dir)

    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    results: List[Dict] = []
    skipped: List[str] = []

    for pdf_path in pdf_files:
        try:
            prefix, algo_name = parse_pdf_filename(pdf_path.name)
        except ValueError:
            print(f"Skip files that cannot be parsed: {pdf_path.name}")
            skipped.append(pdf_path.name)
            continue

        gt_path = gt_dir / f"{prefix}.json"
        if not gt_path.exists():
            print(f"Could not find a matching GT: {gt_path.name}, skip {pdf_path.name}")
            skipped.append(pdf_path.name)
            continue

        algo_out_dir = out_dir / algo_name
        try:
            score_json_path = evaluate_single_pdf(pdf_path, gt_path, algo_out_dir)
            results.append(json.loads(score_json_path.read_text("utf-8")))
            print(f"Finish: {pdf_path.name}")
        except Exception as e:
            print(f"Evaluation failed {pdf_path.name}: {e}")
            skipped.append(pdf_path.name)

    if results:
\
        fields = [
            "precision", "recall", "design_score", "blank_score",
            "readability", "align", "step", "final_raw", "final"
        ]
        avg_dict: Dict[str, float] = {
            f"avg_{f}": round(sum(r[f] for r in results) / len(results), 4)
            for f in fields
        }
        avg_final_score = avg_dict["avg_final"]
    else:
        avg_dict = {f"avg_{f}": 0.0 for f in [
            "precision", "recall", "design_score", "blank_score",
            "readability", "align", "step", "final_raw", "final"
        ]}
        avg_final_score = 0.0

    summary = {
        "total_pdf": len(pdf_files),
        "evaluated": len(results),
        "skipped":   skipped,
        **avg_dict,            
        "details":   results,
    }

    summary_dir = out_dir / "summary"       
    ensure_out_dir(summary_dir)             
    summary_path = summary_dir / "summary.json" 
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), "utf-8")


    print("\n================== Batch evaluation completed ==================")
    print("Average metrics (successfully evaluated files)")
    for fld in [
        "precision", "recall", "design_score", "blank_score",
        "readability", "align", "step", "final_raw", "final"
    ]:
        print(f"  {fld:<12}: {avg_dict[f'avg_{fld}']}")
    print(f"Average final score (avg_final): {avg_final_score}")
    print(f"Detailed results are written to: {summary_path}")
    return summary_path

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Script for Evaluating Scientific Research Drawings\n"
            "• Single file mode: script.py <pdf> <gt.json> [--outdir DIR]\n"
            "• Batch mode : script.py --pdf_dir DIR --gt_dir DIR [--outdir DIR]"
        )
    )

    parser.add_argument("pdf", nargs="?", help="PDF file to be evaluated")
    parser.add_argument("gt_prompt", nargs="?", help="GT prompt json file")

    parser.add_argument("--pdf_dir", help="Folder containing PDFs to be evaluated")
    parser.add_argument("--gt_dir",  help="Folder containing GT json")
 
    parser.add_argument("--outdir", default="eval_output",
                        help="Output directory for intermediate files and score.json / summary.json")
    args = parser.parse_args()
    out_dir = Path(args.outdir).expanduser().resolve()

    if args.pdf_dir and args.gt_dir:
        pdf_dir = Path(args.pdf_dir).expanduser().resolve()
        gt_dir  = Path(args.gt_dir).expanduser().resolve()

        if not pdf_dir.exists() or not pdf_dir.is_dir():
            sys.exit(f"The pdf_dir does not exist or is not a folder: {pdf_dir}")
        if not gt_dir.exists() or not gt_dir.is_dir():
            sys.exit(f"The gt_dir does not exist or is not a folder: {gt_dir}")

        evaluate_batch(pdf_dir, gt_dir, out_dir)
        return  

    if not (args.pdf and args.gt_prompt):
        parser.print_help()
        sys.exit("\nInsufficient parameters: Please provide a single file <pdf> <gt.json>, or use the batch mode with --pdf_dir and --gt_dir.")

    pdf_path       = Path(args.pdf).expanduser().resolve()
    gt_prompt_path = Path(args.gt_prompt).expanduser().resolve()

    if not pdf_path.exists():
        sys.exit(f"NO PDF : {pdf_path}")
    if not gt_prompt_path.exists():
        sys.exit(f"NO GT prompt : {gt_prompt_path}")

    score_json = evaluate_single_pdf(pdf_path, gt_prompt_path, out_dir)
    print("\n================== Evaluation completed ==================")
    print(score_json.read_text("utf-8"))
    print(f"\nAll files have been output to {out_dir}")


if __name__ == "__main__":
    main()


# # —— Single PDF evaluation
# python eval_signal.py some.pdf some_gt.json --outdir ./out_single

# # —— Batch evaluation
# python eval_signal.py --pdf_dir ./result_pdfs --gt_dir ./gt_jsons --outdir ./eval_output