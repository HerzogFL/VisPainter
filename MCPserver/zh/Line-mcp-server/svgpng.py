import os
import cairosvg

def svg_to_png_batch(svg_folder: str, png_folder: str, dpi: int = 300):
    """
    将SVG文件夹中的所有文件转换为PNG
    
    参数:
    - svg_folder: SVG文件所在文件夹
    - png_folder: PNG文件输出文件夹
    - dpi: 输出分辨率，值越高图片越清晰
    """

    os.makedirs(png_folder, exist_ok=True)
    

    for filename in os.listdir(svg_folder):
        if filename.endswith('.svg'):
            svg_path = os.path.join(svg_folder, filename)
            png_path = os.path.join(png_folder, filename.replace('.svg', '.png'))
            
            try:

                cairosvg.svg2png(url=svg_path, write_to=png_path, dpi=dpi)
                print(f"成功转换: {svg_path} -> {png_path}")
            except Exception as e:
                print(f"转换失败: {svg_path}, 错误: {str(e)}")

if __name__ == "__main__":
    svg_folder = r"G:\MCP\MCP-visio\icons"  
    png_folder = r"G:\MCP\MCP-visio\icons_png" 
    
    svg_to_png_batch(svg_folder, png_folder, dpi=300)