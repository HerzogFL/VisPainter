import win32com.client
import os

def get_visio_component_positions():
    try:

        visio = win32com.client.GetActiveObject("Visio.Application")
        

        if visio.Documents.Count == 0:
            print("没有打开的Visio文档")
            return
        

        doc = visio.ActiveDocument
        page = visio.ActivePage
        
        print(f"文档: {doc.Name}")
        print(f"页面: {page.Name}")
        print("-" * 50)
        
        for shape in page.Shapes:
            shape_id = shape.ID
            shape_name = shape.Name
            shape_type = shape.Type
            

            pin_x = shape.CellsU("PinX").ResultIU
            pin_y = shape.CellsU("PinY").ResultIU
            

            width = shape.CellsU("Width").ResultIU
            height = shape.CellsU("Height").ResultIU
            

            shape_text = shape.Text.strip() if shape.Text else ""
            

            print(f"ID: {shape_id}")
            print(f"名称: {shape_name}")
            print(f"类型: {shape_type}")
            print(f"位置: X={pin_x:.2f} 英寸, Y={pin_y:.2f} 英寸")
            print(f"尺寸: 宽={width:.2f} 英寸, 高={height:.2f} 英寸")
            print(f"文本: {shape_text}")
            print("-" * 50)
            
    except Exception as e:
        print(f"发生错误: {e}")
        print("请确保Visio已打开且有活动文档")

if __name__ == "__main__":
    get_visio_component_positions()    