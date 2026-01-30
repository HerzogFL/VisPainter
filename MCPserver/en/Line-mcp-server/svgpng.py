import os
import cairosvg

def svg_to_png_batch(svg_folder: str, png_folder: str, dpi: int = 300):
    """
    Convert all files in an SVG folder to PNG.
    
    Parameters:
    - svg_folder: Folder containing the SVG files.
    - png_folder: Output folder for the PNG files.
    - dpi: Output resolution; higher values result in clearer images.
    """

    os.makedirs(png_folder, exist_ok=True)
    

    for filename in os.listdir(svg_folder):
        if filename.endswith('.svg'):
            svg_path = os.path.join(svg_folder, filename)
            png_path = os.path.join(png_folder, filename.replace('.svg', '.png'))
            
            try:
                # Perform the conversion using cairosvg
                cairosvg.svg2png(url=svg_path, write_to=png_path, dpi=dpi)
                print(f"Successfully converted: {svg_path} -> {png_path}")
            except Exception as e:
                print(f"Conversion failed: {svg_path}, Error: {str(e)}")

if __name__ == "__main__":
    svg_folder = r"G:\MCP\MCP-visio\icons"  
    png_folder = r"G:\MCP\MCP-visio\icons_png" 
    
    svg_to_png_batch(svg_folder, png_folder, dpi=300)