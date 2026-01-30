import win32com.client
import os

def get_visio_component_positions():
    try:
        # Get the active Visio application instance
        visio = win32com.client.GetActiveObject("Visio.Application")
        
        # Check if there are any open documents
        if visio.Documents.Count == 0:
            print("No open Visio documents found.")
            return
        
        doc = visio.ActiveDocument
        page = visio.ActivePage
        
        print(f"Document: {doc.Name}")
        print(f"Page: {page.Name}")
        print("-" * 50)
        
        for shape in page.Shapes:
            shape_id = shape.ID
            shape_name = shape.Name
            shape_type = shape.Type
            
            # Get the center position of the shape (PinX and PinY)
            pin_x = shape.CellsU("PinX").ResultIU
            pin_y = shape.CellsU("PinY").ResultIU
            
            # Get the dimensions of the shape
            width = shape.CellsU("Width").ResultIU
            height = shape.CellsU("Height").ResultIU
            
            # Get the text content of the shape
            shape_text = shape.Text.strip() if shape.Text else ""
            
            print(f"ID: {shape_id}")
            print(f"Name: {shape_name}")
            print(f"Type: {shape_type}")
            print(f"Position: X={pin_x:.2f} inches, Y={pin_y:.2f} inches")
            print(f"Size: Width={width:.2f} inches, Height={height:.2f} inches")
            print(f"Text: {shape_text}")
            print("-" * 50)
            
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure Visio is open and has an active document.")

if __name__ == "__main__":
    get_visio_component_positions()