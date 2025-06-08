import pygame
import pygame_gui
import os
import sys
import json
from typing import List, Tuple, Optional
from pathlib import Path

from spritesheet_model import SpritesheetModel, SpriteData, Point
from sprite_analysis import SpriteAnalyzer
from sprite_renderer import SpriteRenderer

# Initialize Pygame
pygame.init()

# Constants - Made 600 pixels wider
WINDOW_WIDTH = 2400  # Was 1800, now 2400
WINDOW_HEIGHT = 1200
LEFT_PANEL_WIDTH = 350
RIGHT_PANEL_WIDTH = 350
DRAWING_AREA_WIDTH = WINDOW_WIDTH - LEFT_PANEL_WIDTH - RIGHT_PANEL_WIDTH
DRAWING_AREA_HEIGHT = WINDOW_HEIGHT

DEFAULT_SPRITESHEET_DIR = r"C:\Users\Tommaso\Documents\Dev\Spriter\tiles\isometric_tiles\blocks"
DEFAULT_SAVE_DIR = r"C:\Users\Tommaso\Documents\Dev\Spriter\analysis_data"


class FileOperationsPanel:
    """Component for file operations and basic controls"""
    
    def __init__(self, manager, start_x, start_y, panel_width):
        self.manager = manager
        self.start_x = start_x
        self.start_y = start_y
        self.panel_width = panel_width
        self.components = {}
        self.create_components()
    
    def create_components(self):
        current_y = self.start_y + 10
        
        # File operations
        self.components['file_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 150, 30),
            text='Load Spritesheet',
            manager=self.manager
        )
        
        self.components['save_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 170, current_y, 80, 30),
            text='Save',
            manager=self.manager
        )
        
        self.components['load_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 260, current_y, 80, 30),
            text='Load',
            manager=self.manager
        )
        current_y += 40
        
        # Grid configuration
        self.components['rows_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 80, 25),
            text='Rows:',
            manager=self.manager
        )
        self.components['rows_input'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(self.start_x + 95, current_y, 235, 25),
            manager=self.manager
        )
        self.components['rows_input'].set_text('1')
        current_y += 30
        
        self.components['cols_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 80, 25),
            text='Columns:',
            manager=self.manager
        )
        self.components['cols_input'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(self.start_x + 95, current_y, 235, 25),
            manager=self.manager
        )
        self.components['cols_input'].set_text('4')
        current_y += 35
        
        # Split button
        self.components['split_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 35),
            text='Split Spritesheet',
            manager=self.manager
        )
        current_y += 45
        
        self.height = current_y - self.start_y


class AnalysisControlsPanel:
    """Component for analysis controls and settings"""
    
    def __init__(self, manager, start_x, start_y, panel_width):
        self.manager = manager
        self.start_x = start_x
        self.start_y = start_y
        self.panel_width = panel_width
        self.components = {}
        self.create_components()
    
    def create_components(self):
        current_y = self.start_y
        
        # Alpha threshold
        self.components['threshold_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 25),
            text='Alpha Threshold: 0',
            manager=self.manager
        )
        current_y += 30
        
        self.components['threshold_slider'] = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 20),
            start_value=0,
            value_range=(0, 255),
            manager=self.manager
        )
        current_y += 35
        
        # Global Z offset
        self.components['global_z_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 140, 25),
            text='Global Z Offset:',
            manager=self.manager
        )
        self.components['global_z_input'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(self.start_x + 155, current_y, 175, 25),
            manager=self.manager
        )
        self.components['global_z_input'].set_text('0')
        current_y += 35
        
        # Frame-specific Z offset
        self.components['frame_z_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 140, 25),
            text='Frame Z Offset:',
            manager=self.manager
        )
        self.components['frame_z_input'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(self.start_x + 155, current_y, 175, 25),
            manager=self.manager
        )
        self.components['frame_z_input'].set_text('0')
        current_y += 35
        
        # Toggle buttons
        self.components['overlay_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 30),
            text='Toggle Overlay: ON',
            manager=self.manager
        )
        current_y += 35
        
        self.components['diamond_height_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 30),
            text='Diamond Height: ON',
            manager=self.manager
        )
        current_y += 35
        
        self.components['upper_lines_mode_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 30),
            text='Upper Lines: Contact Points',
            manager=self.manager
        )
        current_y += 35
        
        self.components['diamond_vertices_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 30),
            text='Diamond Vertices: OFF',
            manager=self.manager
        )
        current_y += 35
        
        self.components['diamond_lines_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 30),
            text='Diamond Lines: OFF',
            manager=self.manager
        )
        current_y += 35
        
        self.components['raycast_analysis_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 30),
            text='Raycast Analysis: ON',
            manager=self.manager
        )
        current_y += 35
        
        self.components['manual_vertex_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 30),
            text='Manual Vertex Mode: OFF',
            manager=self.manager
        )
        current_y += 35
        
        # Auto-populate button (initially hidden)
        self.components['auto_populate_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 30),
            text='Auto-Populate Vertices',
            manager=self.manager
        )
        self.components['auto_populate_button'].visible = False
        current_y += 35
        
        # Manual vertex controls (initially hidden)
        self.components['vertex_info_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 50),
            text='Selected: Lower North (1)\nKeys: 1234=NSEW F1/F2=Lower/Upper\nRight-click to position',
            manager=self.manager
        )
        self.components['vertex_info_label'].visible = False
        current_y += 60
        
        self.height = current_y - self.start_y


class NavigationPanel:
    """Component for sprite navigation"""
    
    def __init__(self, manager, start_x, start_y, panel_width):
        self.manager = manager
        self.start_x = start_x
        self.start_y = start_y
        self.panel_width = panel_width
        self.components = {}
        self.create_components()
    
    def create_components(self):
        current_y = self.start_y
        
        # Navigation buttons
        self.components['prev_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 150, 35),
            text='< Prev',
            manager=self.manager
        )
        self.components['next_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 170, current_y, 160, 35),
            text='Next >',
            manager=self.manager
        )
        current_y += 45
        
        # Sprite info
        self.components['sprite_info_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 25),
            text='Sprite: 0/0',
            manager=self.manager
        )
        current_y += 30
        
        self.components['pixel_count_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 25),
            text='Pixels above threshold: 0',
            manager=self.manager
        )
        current_y += 35
        
        self.height = current_y - self.start_y


class BoundingBoxInfoPanel:
    """Component for bounding box information"""
    
    def __init__(self, manager, start_x, start_y, panel_width):
        self.manager = manager
        self.start_x = start_x
        self.start_y = start_y
        self.panel_width = panel_width
        self.components = {}
        self.create_components()
    
    def create_components(self):
        current_y = self.start_y
        
        # Bounding box info
        self.components['bbox_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 50),
            text='Bounding Box:\nSize: 0x0\nPosition: (0, 0)',
            manager=self.manager
        )
        current_y += 55
        
        # Size comparison info
        self.components['size_info_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 50),
            text='Original: 0x0\nCropped: 0x0\nSavings: 0%',
            manager=self.manager
        )
        current_y += 60
        
        self.height = current_y - self.start_y


class ViewControlsPanel:
    """Component for view and pixeloid controls"""
    
    def __init__(self, manager, start_x, start_y, panel_width):
        self.manager = manager
        self.start_x = start_x
        self.start_y = start_y
        self.panel_width = panel_width
        self.components = {}
        self.create_components()
    
    def create_components(self):
        current_y = self.start_y
        
        # Pixeloid controls
        self.components['pixeloid_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 25),
            text='Pixeloid: 1x',
            manager=self.manager
        )
        current_y += 30
        
        self.components['pixeloid_up_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 150, 30),
            text='Pixeloid +',
            manager=self.manager
        )
        self.components['pixeloid_down_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 170, current_y, 160, 30),
            text='Pixeloid -',
            manager=self.manager
        )
        current_y += 35
        
        self.components['pixeloid_reset_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 150, 30),
            text='Reset View',
            manager=self.manager
        )
        self.components['center_view_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 170, current_y, 160, 30),
            text='Center View',
            manager=self.manager
        )
        current_y += 35
        
        # Pan info
        self.components['pan_info_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 25),
            text='Pan: Use WASD to move',
            manager=self.manager
        )
        current_y += 30
        
        self.height = current_y - self.start_y


class DetailedMeasurementsPanel:
    """Component for detailed measurements display"""
    
    def __init__(self, manager, start_x, start_y, panel_width):
        self.manager = manager
        self.start_x = start_x
        self.start_y = start_y
        self.panel_width = panel_width
        self.components = {}
        self.create_components()
    
    def create_components(self):
        current_y = self.start_y
        
        # Asset Type Section
        self.components['asset_type_title'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, self.panel_width - 20, 25),
            text='═══ ASSET TYPE ═══',
            manager=self.manager
        )
        current_y += 30
        
        self.components['asset_type'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, self.panel_width - 20, 25),
            text='Type: TILE',
            manager=self.manager
        )
        current_y += 35
        
        # Precise Offsets Section
        self.components['precise_title'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, self.panel_width - 20, 25),
            text='═══ PRECISE OFFSETS ═══',
            manager=self.manager
        )
        current_y += 30
        
        self.components['offsets'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, self.panel_width - 20, 25),
            text='Top:0 Bot:0 Left:0 Right:0',
            manager=self.manager
        )
        current_y += 30
        
        # Diamond Measurements Section
        self.components['diamond_title'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, self.panel_width - 20, 25),
            text='═══ DIAMOND INFO ═══',
            manager=self.manager
        )
        current_y += 30
        
        self.components['diamond_height'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, self.panel_width - 20, 25),
            text='Diamond Height: 0px',
            manager=self.manager
        )
        current_y += 25
        
        self.components['flat_height'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, self.panel_width - 20, 25),
            text='Flat Height: 0px',
            manager=self.manager
        )
        current_y += 25
        
        self.components['diamond_width'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, self.panel_width - 20, 25),
            text='Diamond Width: 0px',
            manager=self.manager
        )
        current_y += 25
        
        self.components['total_height'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, self.panel_width - 20, 25),
            text='Total Height: 0px',
            manager=self.manager
        )
        current_y += 35
        
        # Lower Diamond Vertices Section
        self.components['lower_diamond_title'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, self.panel_width - 20, 25),
            text='═══ LOWER DIAMOND ═══',
            manager=self.manager
        )
        current_y += 30
        
        self.components['lower_vertices'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, self.panel_width - 20, 100),
            text='N:(0,0) S:(0,0)\nE:(0,0) W:(0,0)\nCenter:(0,0)\nZ-Offset:0px',
            manager=self.manager
        )
        current_y += 105
        
        # Upper Diamond Vertices Section
        self.components['upper_diamond_title'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, self.panel_width - 20, 25),
            text='═══ UPPER DIAMOND ═══',
            manager=self.manager
        )
        current_y += 30
        
        self.components['upper_vertices'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, self.panel_width - 20, 100),
            text='N:(0,0) S:(0,0)\nE:(0,0) W:(0,0)\nCenter:(0,0)\nZ-Offset:0px',
            manager=self.manager
        )
        current_y += 105
        
        # Contact Points Section
        self.components['contact_title'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, self.panel_width - 20, 25),
            text='═══ CONTACT POINTS ═══',
            manager=self.manager
        )
        current_y += 30
        
        self.components['contacts_info'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, self.panel_width - 20, 75),
            text='Original Space:\nTop L:(0,0) R:(0,0)\nBot L:(0,0) R:(0,0)\nLeft T:(0,0) B:(0,0)\nRight T:(0,0) B:(0,0)',
            manager=self.manager
        )
        current_y += 80
        
        self.height = current_y - self.start_y
    
    def update_data_from_model(self, sprite_data: Optional[SpriteData], ui_instance=None):
        """Update all components with data from the model"""
        if not sprite_data or not sprite_data.bbox:
            self.set_no_data()
            return
        
        bbox = sprite_data.bbox
        diamond_info = sprite_data.diamond_info
        detailed_analysis = sprite_data.detailed_analysis
        
        # Update asset type
        self.components['asset_type'].set_text(f'Type: {sprite_data.asset_type.value.upper()}')
        
        # Update precise offsets
        edge_offsets = sprite_data.get_edge_offsets()
        self.components['offsets'].set_text(
            f'T:{edge_offsets["top"]} B:{edge_offsets["bottom"]} '
            f'L:{edge_offsets["left"]} R:{edge_offsets["right"]}'
        )
        
        # Update diamond info
        if diamond_info:
            self.components['diamond_height'].set_text(f'Diamond Height: {diamond_info.diamond_height:.1f}px')
            self.components['flat_height'].set_text(f'Flat Height: {diamond_info.predicted_flat_height:.1f}px')
            self.components['diamond_width'].set_text(f'Diamond Width: {diamond_info.diamond_width:.1f}px')
            total_height_text = f'Total Height: {bbox.height}px'
            if diamond_info.upper_z_line_y:
                total_height_text += f' (Z-{int(diamond_info.upper_z_line_y - bbox.y)})'
            self.components['total_height'].set_text(total_height_text)
            
            # Get manual vertex overrides if UI instance is available
            manual_overrides = {}
            if ui_instance and hasattr(ui_instance, 'renderer') and hasattr(ui_instance.renderer, 'manual_vertices') and hasattr(ui_instance.model, 'current_sprite_index'):
                sprite_key = ui_instance.model.current_sprite_index
                manual_overrides = ui_instance.renderer.manual_vertices.get(sprite_key, {})
            
            # Update lower diamond vertices (check for manual overrides)
            lower = diamond_info.lower_diamond
            manual_lower = manual_overrides.get('lower', {})
            
            # Build lower vertices text with manual/algorithmic indicators
            def get_vertex_coords(vertex, vertex_name_key, manual_dict):
                if vertex_name_key in manual_dict:
                    x, y = manual_dict[vertex_name_key]
                    return f'({x},{y})*'  # * indicates manual
                elif vertex:
                    return f'({vertex.x},{vertex.y})'
                else:
                    return '(N/A,N/A)'
            
            lower_text = f'N:{get_vertex_coords(lower.north_vertex, "north", manual_lower)} '
            lower_text += f'S:{get_vertex_coords(lower.south_vertex, "south", manual_lower)}\n'
            lower_text += f'E:{get_vertex_coords(lower.east_vertex, "east", manual_lower)} '
            lower_text += f'W:{get_vertex_coords(lower.west_vertex, "west", manual_lower)}\n'
            lower_text += f'Center:({lower.center.x},{lower.center.y})\n'
            lower_text += f'Z-Offset:{lower.z_offset:.1f}px'
            if manual_lower:
                lower_text += '\n*=Manual'
            self.components['lower_vertices'].set_text(lower_text)
            
            # Update upper diamond vertices (check for manual overrides)
            if diamond_info.upper_diamond:
                upper = diamond_info.upper_diamond
                manual_upper = manual_overrides.get('upper', {})
                
                upper_text = f'N:{get_vertex_coords(upper.north_vertex, "north", manual_upper)} '
                upper_text += f'S:{get_vertex_coords(upper.south_vertex, "south", manual_upper)}\n'
                upper_text += f'E:{get_vertex_coords(upper.east_vertex, "east", manual_upper)} '
                upper_text += f'W:{get_vertex_coords(upper.west_vertex, "west", manual_upper)}\n'
                upper_text += f'Center:({upper.center.x},{upper.center.y})\n'
                upper_text += f'Z-Offset:{upper.z_offset:.1f}px'
                if manual_upper:
                    upper_text += '\n*=Manual'
                self.components['upper_vertices'].set_text(upper_text)
            else:
                self.components['upper_vertices'].set_text('No upper diamond\n(upper_z_offset = 0)')
        else:
            self.components['diamond_height'].set_text('Diamond Height: N/A')
            self.components['flat_height'].set_text('Flat Height: N/A')
            self.components['diamond_width'].set_text('Diamond Width: N/A')
            self.components['total_height'].set_text(f'Total Height: {bbox.height}px')
            self.components['lower_vertices'].set_text('No analysis data')
            self.components['upper_vertices'].set_text('No analysis data')
        
        # Update contact points in original space
        if detailed_analysis and detailed_analysis.contact_points_data:
            contacts = detailed_analysis.contact_points_data.edge_contacts_original
            contact_text = f'Original Space:\n'
            contact_text += f'Top L:({contacts.top_from_left.x if contacts.top_from_left else "N/A"},{contacts.top_from_left.y if contacts.top_from_left else "N/A"}) '
            contact_text += f'R:({contacts.top_from_right.x if contacts.top_from_right else "N/A"},{contacts.top_from_right.y if contacts.top_from_right else "N/A"})\n'
            contact_text += f'Bot L:({contacts.bottom_from_left.x if contacts.bottom_from_left else "N/A"},{contacts.bottom_from_left.y if contacts.bottom_from_left else "N/A"}) '
            contact_text += f'R:({contacts.bottom_from_right.x if contacts.bottom_from_right else "N/A"},{contacts.bottom_from_right.y if contacts.bottom_from_right else "N/A"})\n'
            contact_text += f'Left T:({contacts.left_from_top.x if contacts.left_from_top else "N/A"},{contacts.left_from_top.y if contacts.left_from_top else "N/A"}) '
            contact_text += f'B:({contacts.left_from_bottom.x if contacts.left_from_bottom else "N/A"},{contacts.left_from_bottom.y if contacts.left_from_bottom else "N/A"})\n'
            contact_text += f'Right T:({contacts.right_from_top.x if contacts.right_from_top else "N/A"},{contacts.right_from_top.y if contacts.right_from_top else "N/A"}) '
            contact_text += f'B:({contacts.right_from_bottom.x if contacts.right_from_bottom else "N/A"},{contacts.right_from_bottom.y if contacts.right_from_bottom else "N/A"})'
            self.components['contacts_info'].set_text(contact_text)
        else:
            self.components['contacts_info'].set_text('Original Space:\nNo analysis data available')
    
    def set_no_data(self):
        """Set all components to show no data available"""
        self.components['asset_type'].set_text('Type: N/A')
        self.components['offsets'].set_text('T:N/A B:N/A L:N/A R:N/A')
        self.components['diamond_height'].set_text('Diamond Height: N/A')
        self.components['flat_height'].set_text('Flat Height: N/A')
        self.components['diamond_width'].set_text('Diamond Width: N/A')
        self.components['total_height'].set_text('Total Height: N/A')
        self.components['lower_vertices'].set_text('No analysis data')
        self.components['upper_vertices'].set_text('No analysis data')
        self.components['contacts_info'].set_text('Original Space:\nNo analysis data available')


class AdvancedSpritesheetUI:
    """Advanced UI with two sidebars and modular components - MODULAR VERSION"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Advanced Spritesheet Alpha Analyzer - MODULAR")
        
        self.clock = pygame.time.Clock()
        self.manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Core components
        self.model: Optional[SpritesheetModel] = None
        self.analyzer: Optional[SpriteAnalyzer] = None
        self.spritesheet_surface: Optional[pygame.Surface] = None
        
        # Initialize the renderer module
        self.renderer = SpriteRenderer(DRAWING_AREA_WIDTH, DRAWING_AREA_HEIGHT, LEFT_PANEL_WIDTH)
        
        # UI state
        self.keys_pressed = set()
        
        # Mouse position tracking for pixeloid display
        self.mouse_x = 0
        self.mouse_y = 0
        self.sprite_pixel_x = 0
        self.sprite_pixel_y = 0
        self.mouse_in_drawing_area = False
        
        # Create UI panels
        self.setup_ui_panels()
        
        # Ensure save directory exists
        Path(DEFAULT_SAVE_DIR).mkdir(parents=True, exist_ok=True)
    
    def setup_ui_panels(self):
        """Set up all UI panels in both sidebars"""
        # Left sidebar panels
        current_y = 0
        
        self.file_ops_panel = FileOperationsPanel(self.manager, 0, current_y, LEFT_PANEL_WIDTH)
        current_y += self.file_ops_panel.height + 10
        
        self.analysis_controls_panel = AnalysisControlsPanel(self.manager, 0, current_y, LEFT_PANEL_WIDTH)
        current_y += self.analysis_controls_panel.height + 10
        
        self.navigation_panel = NavigationPanel(self.manager, 0, current_y, LEFT_PANEL_WIDTH)
        current_y += self.navigation_panel.height + 10
        
        self.bbox_info_panel = BoundingBoxInfoPanel(self.manager, 0, current_y, LEFT_PANEL_WIDTH)
        
        # Right sidebar panels
        right_start_x = LEFT_PANEL_WIDTH + DRAWING_AREA_WIDTH
        current_y = 0
        
        self.view_controls_panel = ViewControlsPanel(self.manager, right_start_x, current_y, RIGHT_PANEL_WIDTH)
        current_y += self.view_controls_panel.height + 10
        
        self.detailed_measurements_panel = DetailedMeasurementsPanel(self.manager, right_start_x, current_y, RIGHT_PANEL_WIDTH)
    
    def get_all_ui_elements(self):
        """Get all UI elements for event handling"""
        elements = {}
        
        # Collect from all panels
        for panel_name, panel in [
            ('file_ops', self.file_ops_panel),
            ('analysis', self.analysis_controls_panel),
            ('navigation', self.navigation_panel),
            ('bbox', self.bbox_info_panel),
            ('view', self.view_controls_panel),
            ('measurements', self.detailed_measurements_panel)
        ]:
            for element_name, element in panel.components.items():
                elements[f'{panel_name}_{element_name}'] = element
        
        return elements
    
    def load_spritesheet(self, path: str):
        """Load a spritesheet from file"""
        try:
            surface = pygame.image.load(path).convert_alpha()
            self.spritesheet_surface = surface
            
            # Clear cache when new spritesheet is loaded
            self.renderer._clear_sprite_display_cache()
            
            # Reset manual vertex state for new image
            self.renderer.manual_vertices = {}
            self.renderer.manual_vertex_mode = False
            self.analysis_controls_panel.components['manual_vertex_button'].set_text('Manual Vertex Mode: OFF')
            self.analysis_controls_panel.components['vertex_info_label'].visible = False
            
            # Reset UI inputs to default values for new file
            self.file_ops_panel.components['rows_input'].set_text('1')
            self.file_ops_panel.components['cols_input'].set_text('4')
            self.analysis_controls_panel.components['threshold_slider'].set_current_value(0)
            self.analysis_controls_panel.components['global_z_input'].set_text('0')
            self.analysis_controls_panel.components['frame_z_input'].set_text('0')
            
            print(f"Successfully loaded: {path}")
            return True
        except Exception as e:
            print(f"Failed to load spritesheet: {e}")
            return False
    
    def create_model_from_inputs(self, image_path: str):
        """Create a new model from current UI inputs"""
        try:
            rows = int(self.file_ops_panel.components['rows_input'].get_text())
            cols = int(self.file_ops_panel.components['cols_input'].get_text())
            
            if rows <= 0 or cols <= 0:
                print(f"Invalid grid size: {rows}x{cols}")
                return False
            
            if not self.spritesheet_surface:
                print("No spritesheet loaded")
                return False
            
            total_width = self.spritesheet_surface.get_width()
            total_height = self.spritesheet_surface.get_height()
            
            self.model = SpritesheetModel.create_from_image(
                image_path, rows, cols, total_width, total_height
            )
            
            # Apply current UI settings
            self.model.alpha_threshold = int(self.analysis_controls_panel.components['threshold_slider'].get_current_value())
            self.model.upper_z_offset = int(self.analysis_controls_panel.components['global_z_input'].get_text() or '0')
            self.model.show_overlay = True
            self.model.show_diamond_height = True
            
            # Create analyzer and load surface
            self.analyzer = SpriteAnalyzer(self.model)
            self.analyzer.load_spritesheet_surface(self.spritesheet_surface)
            
            # Reset UI state
            self.model.current_sprite_index = 0
            self.model.pixeloid_multiplier = 1
            self.model.pan_x = 0
            self.model.pan_y = 0
            
            # Clear cache when new model is created
            self.renderer._clear_sprite_display_cache()
            
            self.update_sprite_info()
            print(f"Created model with {len(self.model.sprites)} sprites ({rows}x{cols})")
            return True
            
        except ValueError as e:
            print(f"Invalid input values: {e}")
            return False
        except Exception as e:
            print(f"Error creating model: {e}")
            return False
    
    def update_sprite_info(self):
        """Update sprite information displays"""
        if not self.model or not self.analyzer:
            self.clear_sprite_info()
            return
        
        current_sprite = self.model.get_current_sprite()
        if not current_sprite:
            self.clear_sprite_info()
            return
        
        # Update sprite counter
        self.navigation_panel.components['sprite_info_label'].set_text(
            f'Sprite: {self.model.current_sprite_index + 1}/{len(self.model.sprites)}'
        )
        
        # Analyze current sprite if not already analyzed
        if current_sprite.pixel_count is None:
            self.analyzer.analyze_sprite(self.model.current_sprite_index)
        
        # Update pixel count
        pixel_count = current_sprite.pixel_count or 0
        self.navigation_panel.components['pixel_count_label'].set_text(f'Pixels above threshold: {pixel_count}')
        
        # Update bounding box info
        if current_sprite.bbox:
            bbox = current_sprite.bbox
            self.bbox_info_panel.components['bbox_label'].set_text(
                f'Bounding Box:\nSize: {bbox.width}x{bbox.height}\nPosition: ({bbox.x}, {bbox.y})'
            )
            
            # Update size comparison
            savings_percent = current_sprite.calculate_savings_percent()
            original_size = current_sprite.original_size
            self.bbox_info_panel.components['size_info_label'].set_text(
                f'Original: {original_size[0]}x{original_size[1]}\n'
                f'Cropped: {bbox.width}x{bbox.height}\n'
                f'Savings: {savings_percent:.1f}%'
            )
        else:
            self.bbox_info_panel.components['bbox_label'].set_text('Bounding Box:\nNo pixels above threshold')
            original_size = current_sprite.original_size
            self.bbox_info_panel.components['size_info_label'].set_text(
                f'Original: {original_size[0]}x{original_size[1]}\nCropped: N/A\nSavings: N/A'
            )
        
        # Update detailed measurements
        self.detailed_measurements_panel.update_data_from_model(current_sprite, self)
        
        # Update frame-specific Z offset
        frame_z_offset = current_sprite.frame_upper_z_offset
        self.analysis_controls_panel.components['frame_z_input'].set_text(str(frame_z_offset))
    
    def clear_sprite_info(self):
        """Clear all sprite information displays"""
        self.navigation_panel.components['sprite_info_label'].set_text('Sprite: 0/0')
        self.navigation_panel.components['pixel_count_label'].set_text('Pixels above threshold: 0')
        self.bbox_info_panel.components['bbox_label'].set_text('Bounding Box:\nN/A')
        self.bbox_info_panel.components['size_info_label'].set_text('Original: N/A\nCropped: N/A\nSavings: N/A')
        self.detailed_measurements_panel.set_no_data()
    
    def handle_frame_z_offset_change(self, text: str):
        """Handle frame-specific Z offset change"""
        if self.model:
            try:
                new_value = int(text) if text else 0
                frame_z_offset = max(0, new_value)
                self.model.set_frame_upper_z_offset(self.model.current_sprite_index, frame_z_offset)
                # Clear cache for this specific sprite since its rendering changed
                self.renderer._clear_sprite_cache(self.model.current_sprite_index)
                self.update_sprite_info()
            except ValueError:
                pass  # Ignore invalid input
    
    def run(self):
        """Main game loop - clean and simple"""
        running = True
        
        while running:
            time_delta = self.clock.tick(60) / 1000.0  # Convert to seconds as pygame_gui expects
            ui_elements = self.get_all_ui_elements()
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                    self.handle_button_press(event, ui_elements)
                elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    self.handle_slider_move(event, ui_elements)
                elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    self.handle_text_change(event, ui_elements)
                elif event.type == pygame.MOUSEWHEEL:
                    self.handle_mouse_wheel(event)
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:  # Right click
                        self.handle_right_click(event)
                elif event.type == pygame.KEYDOWN:
                    self.keys_pressed.add(event.key)
                    # Handle manual vertex mode key commands
                    if self.renderer.manual_vertex_mode:
                        self.handle_manual_vertex_keys(event.key)
                elif event.type == pygame.KEYUP:
                    self.keys_pressed.discard(event.key)
                
                self.manager.process_events(event)
            
            # Update systems
            self.manager.update(time_delta)
            self.update_panning()
            
            # Draw everything
            self.screen.fill((40, 40, 40))
            pygame.draw.rect(self.screen, (60, 60, 60), (0, 0, LEFT_PANEL_WIDTH, WINDOW_HEIGHT))
            pygame.draw.rect(self.screen, (60, 60, 60), (LEFT_PANEL_WIDTH + DRAWING_AREA_WIDTH, 0, RIGHT_PANEL_WIDTH, WINDOW_HEIGHT))
            
            # Use renderer for sprite display
            self.renderer.draw_sprite_display(self.screen, self.model, self.analyzer, LEFT_PANEL_WIDTH)
            self.renderer.draw_mouse_position_display(self.screen, self.model, self.mouse_in_drawing_area,
                                                    self.sprite_pixel_x, self.sprite_pixel_y, WINDOW_WIDTH)
            self.manager.draw_ui(self.screen)
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
    
    def handle_button_press(self, event, ui_elements):
        """Handle button press events"""
        if event.ui_element == ui_elements['file_ops_file_button']:
            self.handle_file_load()
        elif event.ui_element == ui_elements['file_ops_save_button']:
            self.save_analysis_data()
        elif event.ui_element == ui_elements['file_ops_load_button']:
            self.load_analysis_data()
        elif event.ui_element == ui_elements['file_ops_split_button']:
            self.handle_split_spritesheet()
        elif event.ui_element == ui_elements['navigation_prev_button']:
            self.handle_prev_sprite()
        elif event.ui_element == ui_elements['navigation_next_button']:
            self.handle_next_sprite()
        elif event.ui_element == ui_elements['analysis_overlay_button']:
            self.handle_toggle_overlay()
        elif event.ui_element == ui_elements['analysis_diamond_height_button']:
            self.handle_toggle_diamond_height()
        elif event.ui_element == ui_elements['analysis_upper_lines_mode_button']:
            self.handle_toggle_upper_lines_mode()
        elif event.ui_element == ui_elements['analysis_diamond_vertices_button']:
            self.handle_toggle_diamond_vertices()
        elif event.ui_element == ui_elements['analysis_diamond_lines_button']:
            self.handle_toggle_diamond_lines()
        elif event.ui_element == ui_elements['analysis_raycast_analysis_button']:
            self.handle_toggle_raycast_analysis()
        elif event.ui_element == ui_elements['analysis_manual_vertex_button']:
            self.handle_toggle_manual_vertex_mode()
        elif event.ui_element == ui_elements['analysis_auto_populate_button']:
            self.handle_auto_populate_vertices()
        elif event.ui_element == ui_elements['view_pixeloid_up_button']:
            self.handle_pixeloid_up()
        elif event.ui_element == ui_elements['view_pixeloid_down_button']:
            self.handle_pixeloid_down()
        elif event.ui_element == ui_elements['view_pixeloid_reset_button']:
            self.handle_reset_view()
        elif event.ui_element == ui_elements['view_center_view_button']:
            self.handle_center_view()
    
    def handle_slider_move(self, event, ui_elements):
        """Handle slider movement events"""
        if event.ui_element == ui_elements['analysis_threshold_slider']:
            self.handle_threshold_change(int(event.value))
    
    def handle_text_change(self, event, ui_elements):
        """Handle text entry change events"""
        if event.ui_element == ui_elements['analysis_global_z_input']:
            self.handle_global_z_change(event.text)
        elif event.ui_element == ui_elements['analysis_frame_z_input']:
            self.handle_frame_z_offset_change(event.text)
    
    def handle_file_load(self):
        """Handle file loading"""
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            
            initial_dir = DEFAULT_SPRITESHEET_DIR if os.path.exists(DEFAULT_SPRITESHEET_DIR) else None
            
            file_path = filedialog.askopenfilename(
                initialdir=initial_dir,
                title="Select Spritesheet",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            root.destroy()
            
            if file_path:
                if self.load_spritesheet(file_path):
                    self.create_model_from_inputs(file_path)
                else:
                    print("Failed to load spritesheet")
        except Exception as e:
            print(f"Error opening file dialog: {e}")
    
    def handle_split_spritesheet(self):
        """Handle spritesheet splitting"""
        if self.spritesheet_surface:
            image_path = self.model.image_path if self.model else "unknown"
            self.create_model_from_inputs(image_path)
    
    def handle_prev_sprite(self):
        """Handle previous sprite navigation"""
        if self.model and self.model.current_sprite_index > 0:
            self.model.current_sprite_index -= 1
            self.model.pan_x = 0
            self.model.pan_y = 0
            self.update_sprite_info()
    
    def handle_next_sprite(self):
        """Handle next sprite navigation"""
        if self.model and self.model.current_sprite_index < len(self.model.sprites) - 1:
            self.model.current_sprite_index += 1
            self.model.pan_x = 0
            self.model.pan_y = 0
            self.update_sprite_info()
    
    def handle_threshold_change(self, value: int):
        """Handle alpha threshold change"""
        if self.model:
            self.model.update_analysis_settings(alpha_threshold=value)
            self.analysis_controls_panel.components['threshold_label'].set_text(f'Alpha Threshold: {value}')
            # Clear cache since alpha threshold affects sprite rendering
            self.renderer._clear_sprite_display_cache()
            self.update_sprite_info()
    
    def handle_global_z_change(self, text: str):
        """Handle global Z offset change"""
        if self.model:
            try:
                new_value = int(text) if text else 0
                upper_z_offset = max(0, new_value)
                self.model.update_analysis_settings(upper_z_offset=upper_z_offset)
                # Clear cache since Z offset affects analysis and rendering
                self.renderer._clear_sprite_display_cache()
                self.update_sprite_info()
            except ValueError:
                pass  # Ignore invalid input
    
    def handle_toggle_overlay(self):
        """Handle overlay toggle"""
        if self.model:
            self.model.show_overlay = not self.model.show_overlay
            self.analysis_controls_panel.components['overlay_button'].set_text(
                f'Toggle Overlay: {"ON" if self.model.show_overlay else "OFF"}'
            )
            # Clear cache since overlay toggle affects rendering
            self.renderer._clear_sprite_display_cache()
    
    def handle_toggle_diamond_height(self):
        """Handle diamond height toggle"""
        if self.model:
            self.model.show_diamond_height = not self.model.show_diamond_height
            self.analysis_controls_panel.components['diamond_height_button'].set_text(
                f'Diamond Height: {"ON" if self.model.show_diamond_height else "OFF"}'
            )
            # Clear cache since diamond height toggle affects rendering
            self.renderer._clear_sprite_display_cache()
    
    def handle_toggle_upper_lines_mode(self):
        """Handle upper lines mode toggle"""
        if self.model:
            self.model.upper_lines_midpoint_mode = not self.model.upper_lines_midpoint_mode
            mode_text = "Midpoint" if self.model.upper_lines_midpoint_mode else "Contact Points"
            self.analysis_controls_panel.components['upper_lines_mode_button'].set_text(f'Upper Lines: {mode_text}')
            # Use the proper update method to clear analysis data
            self.model.update_analysis_settings(upper_lines_midpoint_mode=self.model.upper_lines_midpoint_mode)
            # Clear cache since upper lines mode affects rendering
            self.renderer._clear_sprite_display_cache()
            self.update_sprite_info()
    
    def handle_toggle_diamond_vertices(self):
        """Handle diamond vertices toggle"""
        if self.model:
            self.model.show_diamond_vertices = not self.model.show_diamond_vertices
            self.analysis_controls_panel.components['diamond_vertices_button'].set_text(
                f'Diamond Vertices: {"ON" if self.model.show_diamond_vertices else "OFF"}'
            )
            
            # Print debug info when toggling
            print(f"\n=== DIAMOND VERTICES TOGGLE: {'ON' if self.model.show_diamond_vertices else 'OFF'} ===")
            
            if self.model.show_diamond_vertices:
                current_sprite = self.model.get_current_sprite()
                if current_sprite and current_sprite.diamond_info:
                    diamond_info = current_sprite.diamond_info
                    print(f"Sprite {self.model.current_sprite_index} Diamond Coordinates:")
                    
                    if diamond_info.lower_diamond:
                        lower = diamond_info.lower_diamond
                        print(f"  LOWER DIAMOND:")
                        print(f"    North: ({lower.north_vertex.x}, {lower.north_vertex.y})")
                        print(f"    South: ({lower.south_vertex.x}, {lower.south_vertex.y})")
                        print(f"    East:  ({lower.east_vertex.x}, {lower.east_vertex.y})")
                        print(f"    West:  ({lower.west_vertex.x}, {lower.west_vertex.y})")
                        print(f"    Center: ({lower.center.x}, {lower.center.y})")
                        print(f"    Z-Offset: {lower.z_offset}")
                    
                    if diamond_info.upper_diamond:
                        upper = diamond_info.upper_diamond
                        print(f"  UPPER DIAMOND:")
                        print(f"    North: ({upper.north_vertex.x}, {upper.north_vertex.y})")
                        print(f"    South: ({upper.south_vertex.x}, {upper.south_vertex.y})")
                        print(f"    East:  ({upper.east_vertex.x}, {upper.east_vertex.y})")
                        print(f"    West:  ({upper.west_vertex.x}, {upper.west_vertex.y})")
                        print(f"    Center: ({upper.center.x}, {upper.center.y})")
                        print(f"    Z-Offset: {upper.z_offset}")
                    else:
                        print("  NO UPPER DIAMOND (upper_z_offset = 0)")
                    
                    if current_sprite.bbox:
                        bbox = current_sprite.bbox
                        print(f"  BBOX: ({bbox.x}, {bbox.y}) size {bbox.width}x{bbox.height}")
                        print(f"  effective_upper_z: {self.model.get_effective_upper_z_offset(self.model.current_sprite_index)}")
                else:
                    print("  No diamond analysis data available")
            
            # Clear cache since diamond vertices toggle affects rendering
            self.renderer._clear_sprite_display_cache()
    
    def handle_toggle_diamond_lines(self):
        """Handle diamond lines toggle"""
        self.renderer.show_diamond_lines = not self.renderer.show_diamond_lines
        self.analysis_controls_panel.components['diamond_lines_button'].set_text(
            f'Diamond Lines: {"ON" if self.renderer.show_diamond_lines else "OFF"}'
        )
        
        print(f"Diamond Lines: {'ON' if self.renderer.show_diamond_lines else 'OFF'}")
        
        # Clear cache since diamond lines toggle affects rendering
        self.renderer._clear_sprite_display_cache()
    
    def handle_toggle_raycast_analysis(self):
        """Handle raycast analysis toggle"""
        self.renderer.show_raycast_analysis = not self.renderer.show_raycast_analysis
        self.analysis_controls_panel.components['raycast_analysis_button'].set_text(
            f'Raycast Analysis: {"ON" if self.renderer.show_raycast_analysis else "OFF"}'
        )
        
        print(f"Raycast Analysis: {'ON' if self.renderer.show_raycast_analysis else 'OFF'}")
        
        # Clear cache since raycast analysis toggle affects rendering
        self.renderer._clear_sprite_display_cache()
    
    def handle_toggle_manual_vertex_mode(self):
        """Handle manual vertex mode toggle"""
        if not self.model:
            print("Please load a spritesheet first before using manual vertex mode")
            return
        
        self.renderer.manual_vertex_mode = not self.renderer.manual_vertex_mode
        self.analysis_controls_panel.components['manual_vertex_button'].set_text(
            f'Manual Vertex Mode: {"ON" if self.renderer.manual_vertex_mode else "OFF"}'
        )
        
        # Show/hide vertex selection info and auto-populate button
        self.analysis_controls_panel.components['vertex_info_label'].visible = self.renderer.manual_vertex_mode
        self.analysis_controls_panel.components['auto_populate_button'].visible = self.renderer.manual_vertex_mode
        
        if self.renderer.manual_vertex_mode:
            # Auto-enable diamond vertices display when entering manual mode
            if not self.model.show_diamond_vertices:
                self.model.show_diamond_vertices = True
                self.analysis_controls_panel.components['diamond_vertices_button'].set_text('Diamond Vertices: ON')
            
            # Update info label
            self._update_vertex_info_label()
            print(f"\n=== MANUAL VERTEX MODE: ON ===")
            print(f"Selected: {self.renderer.selected_diamond.title()} {self.renderer._get_vertex_name(self.renderer.selected_vertex)}")
            print("Controls: 1=N, 2=S, 3=E, 4=W, F1=Lower, F2=Upper, Right-click to position")
            print("Auto-Populate: Fill missing vertices from manual ones")
        else:
            print("=== MANUAL VERTEX MODE: OFF ===")
        
        # Force complete cache clear and immediate update when entering manual mode
        self.renderer._clear_sprite_display_cache()
        
        # Also update sprite info to force fresh render
        if self.renderer.manual_vertex_mode:
            self.update_sprite_info()
    
    def _update_vertex_info_label(self):
        """Update the vertex selection info label"""
        if hasattr(self.analysis_controls_panel.components, 'vertex_info_label'):
            vertex_name = self.renderer._get_vertex_name(self.renderer.selected_vertex)
            diamond_name = self.renderer.selected_diamond.title()
            info_text = f'Selected: {diamond_name} {vertex_name} ({self.renderer.selected_vertex})\n'
            info_text += 'Keys: 1234=NSEW F1/F2=Lower/Upper\n'
            info_text += 'Right-click to position'
            self.analysis_controls_panel.components['vertex_info_label'].set_text(info_text)
    
    def handle_manual_vertex_keys(self, key):
        """Handle keyboard input for manual vertex mode"""
        if not self.renderer.manual_vertex_mode:
            return
        
        # Number keys 1-4 for vertex selection (N, S, E, W)
        if key == pygame.K_1:
            self.renderer.selected_vertex = 1  # North
        elif key == pygame.K_2:
            self.renderer.selected_vertex = 2  # South
        elif key == pygame.K_3:
            self.renderer.selected_vertex = 3  # East
        elif key == pygame.K_4:
            self.renderer.selected_vertex = 4  # West
        # F1/F2 for diamond selection
        elif key == pygame.K_F1:
            self.renderer.selected_diamond = 'lower'
        elif key == pygame.K_F2:
            self.renderer.selected_diamond = 'upper'
        else:
            return  # Key not handled
        
        # Update UI and clear cache
        self._update_vertex_info_label()
        vertex_name = self.renderer._get_vertex_name(self.renderer.selected_vertex)
        print(f"Selected: {self.renderer.selected_diamond.title()} {vertex_name} ({self.renderer.selected_vertex})")
        self.renderer._clear_sprite_display_cache()
    
    def handle_right_click(self, event):
        """Handle right-click for manual vertex positioning"""
        if not self.renderer.manual_vertex_mode or not self.model:
            return
        
        mouse_x, mouse_y = event.pos
        drawing_area = pygame.Rect(LEFT_PANEL_WIDTH, 0, DRAWING_AREA_WIDTH, DRAWING_AREA_HEIGHT)
        
        if not drawing_area.collidepoint(mouse_x, mouse_y):
            return  # Click outside drawing area
        
        current_sprite = self.model.get_current_sprite()
        if not current_sprite:
            return
        
        # Convert mouse position to sprite pixel coordinates (same logic as mouse motion)
        mouse_x_in_drawing = mouse_x - LEFT_PANEL_WIDTH
        mouse_y_in_drawing = mouse_y
        
        sprite_rect = pygame.Rect(0, 0, current_sprite.original_size[0], current_sprite.original_size[1])
        display_width = sprite_rect.width * self.model.pixeloid_multiplier
        display_height = sprite_rect.height * self.model.pixeloid_multiplier
        base_sprite_x = (DRAWING_AREA_WIDTH - display_width) // 2
        base_sprite_y = (DRAWING_AREA_HEIGHT - display_height) // 2
        sprite_x = base_sprite_x + self.model.pan_x
        sprite_y = base_sprite_y + self.model.pan_y
        
        # Calculate which sprite pixel was clicked
        sprite_pixel_x = (mouse_x_in_drawing - sprite_x) / self.model.pixeloid_multiplier
        sprite_pixel_y = (mouse_y_in_drawing - sprite_y) / self.model.pixeloid_multiplier
        
        print(f"DEBUG CLICK: mouse_in_drawing=({mouse_x_in_drawing},{mouse_y_in_drawing})")
        print(f"DEBUG CLICK: sprite_pos=({sprite_x},{sprite_y}) pixeloid={self.model.pixeloid_multiplier}")
        print(f"DEBUG CLICK: raw_sprite_pixel=({sprite_pixel_x:.1f},{sprite_pixel_y:.1f})")
        
        # Clamp to sprite bounds
        sprite_pixel_x = max(0, min(current_sprite.original_size[0] - 1, sprite_pixel_x))
        sprite_pixel_y = max(0, min(current_sprite.original_size[1] - 1, sprite_pixel_y))
        
        print(f"DEBUG CLICK: clamped_sprite_pixel=({sprite_pixel_x:.1f},{sprite_pixel_y:.1f})")
        
        # sprite_pixel_x/y are already in absolute coordinates since we display the full sprite
        original_x = int(sprite_pixel_x)
        original_y = int(sprite_pixel_y)
        print(f"DEBUG CLICK: sprite_pixel=({sprite_pixel_x:.1f},{sprite_pixel_y:.1f}) -> absolute=({original_x},{original_y})")
        
        # Store the manual vertex position
        sprite_key = self.model.current_sprite_index
        if sprite_key not in self.renderer.manual_vertices:
            self.renderer.manual_vertices[sprite_key] = {}
        
        if self.renderer.selected_diamond not in self.renderer.manual_vertices[sprite_key]:
            self.renderer.manual_vertices[sprite_key][self.renderer.selected_diamond] = {}
        
        vertex_name = self.renderer._get_vertex_name(self.renderer.selected_vertex).lower()
        self.renderer.manual_vertices[sprite_key][self.renderer.selected_diamond][vertex_name] = (original_x, original_y)
        
        # Log the positioning
        print(f"Positioned {self.renderer.selected_diamond} {vertex_name} at ({original_x}, {original_y}) "
              f"[sprite pixel: ({sprite_pixel_x:.1f}, {sprite_pixel_y:.1f})]")
        print(f"DEBUG STORAGE: manual_vertices after positioning = {self.renderer.manual_vertices}")
        
        # Clear cache to trigger re-render with new vertex position
        self.renderer._clear_sprite_display_cache()
        
        # Update measurements display to show new manual coordinates
        self.update_sprite_info()
    
    def handle_auto_populate_vertices(self):
        """Auto-populate missing vertices based on manual inputs and geometric relationships"""
        if not self.model or not self.renderer.manual_vertex_mode:
            print("Auto-populate requires manual vertex mode to be enabled")
            return
        
        sprite_key = self.model.current_sprite_index
        current_sprite = self.model.get_current_sprite()
        if not current_sprite or not current_sprite.bbox:
            print("No sprite data available for auto-populate")
            return
        
        manual_data = self.renderer.manual_vertices.get(sprite_key, {})
        if not manual_data:
            print("No manual vertices to work with")
            return
        
        bbox = current_sprite.bbox
        width = bbox.width
        
        print(f"\n=== AUTO-POPULATE VERTICES ===")
        print(f"Starting with: {manual_data}")
        
        # Initialize if needed
        if sprite_key not in self.renderer.manual_vertices:
            self.renderer.manual_vertices[sprite_key] = {}
        
        # Step 1: Complete each diamond that has >= 2 points
        for diamond_level in ['lower', 'upper']:
            diamond_data = manual_data.get(diamond_level, {})
            point_count = len(diamond_data)
            
            if point_count >= 2:
                print(f"Completing {diamond_level} diamond ({point_count} points)")
                completed_diamond = self._complete_diamond_from_points(diamond_data, width)
                
                # Update manual vertices with completed diamond
                if diamond_level not in self.renderer.manual_vertices[sprite_key]:
                    self.renderer.manual_vertices[sprite_key][diamond_level] = {}
                self.renderer.manual_vertices[sprite_key][diamond_level].update(completed_diamond)
        
        # Step 2: Handle cross-diamond derivation if needed
        lower_data = self.renderer.manual_vertices[sprite_key].get('lower', {})
        upper_data = self.renderer.manual_vertices[sprite_key].get('upper', {})
        
        lower_complete = len(lower_data) >= 4
        upper_complete = len(upper_data) >= 4
        
        if lower_complete and not upper_complete and len(upper_data) >= 1:
            # Derive z_lower from one upper point and complete upper diamond
            z_lower = self._derive_z_lower_from_diamonds(lower_data, upper_data)
            print(f"Derived z_lower: {z_lower}")
            completed_upper = self._derive_diamond_from_other(lower_data, -z_lower)  # Upper is ABOVE lower (smaller Y)
            
            if 'upper' not in self.renderer.manual_vertices[sprite_key]:
                self.renderer.manual_vertices[sprite_key]['upper'] = {}
            self.renderer.manual_vertices[sprite_key]['upper'].update(completed_upper)
            
        elif upper_complete and not lower_complete and len(lower_data) >= 1:
            # Derive z_lower from one lower point and complete lower diamond
            z_lower = self._derive_z_lower_from_diamonds(upper_data, lower_data)
            print(f"Derived z_lower: {z_lower}")
            completed_lower = self._derive_diamond_from_other(upper_data, z_lower)  # Lower is BELOW upper (larger Y)
            
            if 'lower' not in self.renderer.manual_vertices[sprite_key]:
                self.renderer.manual_vertices[sprite_key]['lower'] = {}
            self.renderer.manual_vertices[sprite_key]['lower'].update(completed_lower)
            
        elif lower_complete and not upper_complete:
            # Use algorithmic z_lower to create upper diamond
            if current_sprite.diamond_info:
                z_lower = current_sprite.diamond_info.lower_z_offset
                print(f"Using algorithmic z_lower: {z_lower}")
                completed_upper = self._derive_diamond_from_other(lower_data, -z_lower)  # Upper is ABOVE lower
                
                if 'upper' not in self.renderer.manual_vertices[sprite_key]:
                    self.renderer.manual_vertices[sprite_key]['upper'] = {}
                self.renderer.manual_vertices[sprite_key]['upper'].update(completed_upper)
                
        elif upper_complete and not lower_complete:
            # Use algorithmic z_lower to create lower diamond
            if current_sprite.diamond_info:
                z_lower = current_sprite.diamond_info.lower_z_offset
                print(f"Using algorithmic z_lower: {z_lower}")
                completed_lower = self._derive_diamond_from_other(upper_data, z_lower)  # Lower is BELOW upper
                
                if 'lower' not in self.renderer.manual_vertices[sprite_key]:
                    self.renderer.manual_vertices[sprite_key]['lower'] = {}
                self.renderer.manual_vertices[sprite_key]['lower'].update(completed_lower)
        
        print(f"Final result: {self.renderer.manual_vertices[sprite_key]}")
        
        # Clear cache and update display
        self.renderer._clear_sprite_display_cache()
        self.update_sprite_info()
    
    def _complete_diamond_from_points(self, diamond_data, width):
        """Complete a diamond using geometric relationships from existing points"""
        completed = {}
        
        # Copy existing points
        for vertex, coords in diamond_data.items():
            completed[vertex] = coords
        
        # Apply geometric relationships to fill missing points
        # NOTE: In screen coords, Y increases downward, so "up" = smaller Y
        if 'south' in diamond_data and 'north' not in completed:
            # North is directly above South by width//2 (smaller Y)
            sx, sy = diamond_data['south']
            completed['north'] = (sx, sy - width // 2)
            
        if 'north' in diamond_data and 'south' not in completed:
            # South is directly below North by width//2 (larger Y)
            nx, ny = diamond_data['north']
            completed['south'] = (nx, ny + width // 2)
            
        if 'west' in diamond_data and 'east' not in completed:
            # East is directly right of West by width
            wx, wy = diamond_data['west']
            completed['east'] = (wx + width, wy)
            
        if 'east' in diamond_data and 'west' not in completed:
            # West is directly left of East by width
            ex, ey = diamond_data['east']
            completed['west'] = (ex - width, ey)
        
        return completed
    
    def _derive_z_lower_from_diamonds(self, complete_diamond, partial_diamond):
        """Derive z_lower (height difference) from corresponding points in two diamonds"""
        # Find a common vertex between the diamonds
        for vertex in complete_diamond:
            if vertex in partial_diamond:
                complete_y = complete_diamond[vertex][1]
                partial_y = partial_diamond[vertex][1]
                return abs(complete_y - partial_y)
        return 0
    
    def _derive_diamond_from_other(self, source_diamond, z_offset):
        """Derive a complete diamond by shifting another diamond by z_offset"""
        derived = {}
        for vertex, (x, y) in source_diamond.items():
            derived[vertex] = (x, y + z_offset)
        return derived
    
    def handle_pixeloid_up(self):
        """Handle pixeloid increase"""
        if self.model:
            self.model.pixeloid_multiplier = min(32, self.model.pixeloid_multiplier * 2)
            self.view_controls_panel.components['pixeloid_label'].set_text(f'Pixeloid: {self.model.pixeloid_multiplier}x')
            # Clear cache since pixeloid affects rendering
            self.renderer._clear_sprite_display_cache()
    
    def handle_pixeloid_down(self):
        """Handle pixeloid decrease"""
        if self.model:
            self.model.pixeloid_multiplier = max(1, self.model.pixeloid_multiplier // 2)
            self.view_controls_panel.components['pixeloid_label'].set_text(f'Pixeloid: {self.model.pixeloid_multiplier}x')
            # Clear cache since pixeloid affects rendering
            self.renderer._clear_sprite_display_cache()
    
    def handle_reset_view(self):
        """Handle view reset"""
        if self.model:
            self.model.pixeloid_multiplier = 1
            self.model.pan_x = 0
            self.model.pan_y = 0
            self.view_controls_panel.components['pixeloid_label'].set_text(f'Pixeloid: {self.model.pixeloid_multiplier}x')
            # Clear cache since pixeloid and pan affects rendering
            self.renderer._clear_sprite_display_cache()
    
    def handle_center_view(self):
        """Handle view centering"""
        if self.model:
            self.model.pan_x = 0
            self.model.pan_y = 0
            # Clear cache since pan affects rendering
            self.renderer._clear_sprite_display_cache()
    
    def handle_mouse_wheel(self, event):
        """Handle mouse wheel for pixeloid adjustment with zoom-to-mouse functionality"""
        if not self.model:
            return
            
        mouse_x, mouse_y = pygame.mouse.get_pos()
        drawing_area = pygame.Rect(LEFT_PANEL_WIDTH, 0, DRAWING_AREA_WIDTH, DRAWING_AREA_HEIGHT)
        if drawing_area.collidepoint(mouse_x, mouse_y):
            # Get current sprite to calculate coordinates
            current_sprite = self.model.get_current_sprite()
            if not current_sprite:
                return
                
            # Convert mouse position to drawing area coordinates
            mouse_x_in_drawing = mouse_x - LEFT_PANEL_WIDTH
            mouse_y_in_drawing = mouse_y
            
            # Calculate current sprite positioning before zoom
            old_pixeloid = self.model.pixeloid_multiplier
            sprite_rect = pygame.Rect(0, 0, current_sprite.original_size[0], current_sprite.original_size[1])
            
            old_display_width = sprite_rect.width * old_pixeloid
            old_display_height = sprite_rect.height * old_pixeloid
            old_base_sprite_x = (DRAWING_AREA_WIDTH - old_display_width) // 2
            old_base_sprite_y = (DRAWING_AREA_HEIGHT - old_display_height) // 2
            old_sprite_x = old_base_sprite_x + self.model.pan_x
            old_sprite_y = old_base_sprite_y + self.model.pan_y
            
            # Calculate which sprite pixel is under the mouse (use ACTUAL sprite position)
            sprite_pixel_x = (mouse_x_in_drawing - old_sprite_x) / old_pixeloid
            sprite_pixel_y = (mouse_y_in_drawing - old_sprite_y) / old_pixeloid
            
            print(f"DEBUG ZOOM: mouse_in_drawing=({mouse_x_in_drawing},{mouse_y_in_drawing})")
            print(f"DEBUG ZOOM: old_sprite_pos=({old_sprite_x},{old_sprite_y}) old_pixeloid={old_pixeloid}")
            print(f"DEBUG ZOOM: targeted_sprite_pixel=({sprite_pixel_x:.1f},{sprite_pixel_y:.1f})")
            
            # Apply zoom
            if event.y > 0:  # Scroll up - increase pixeloid
                new_pixeloid = min(32, self.model.pixeloid_multiplier * 2)
            else:  # Scroll down - decrease pixeloid
                new_pixeloid = max(1, self.model.pixeloid_multiplier // 2)
            
            print(f"DEBUG ZOOM: old_pixeloid={old_pixeloid} -> new_pixeloid={new_pixeloid}")
            
            # Only proceed if pixeloid actually changed
            if new_pixeloid != old_pixeloid:
                old_pan_x = self.model.pan_x
                old_pan_y = self.model.pan_y
                
                self.model.pixeloid_multiplier = new_pixeloid
                
                # Calculate new sprite positioning after zoom
                new_display_width = sprite_rect.width * new_pixeloid
                new_display_height = sprite_rect.height * new_pixeloid
                new_base_sprite_x = (DRAWING_AREA_WIDTH - new_display_width) // 2
                new_base_sprite_y = (DRAWING_AREA_HEIGHT - new_display_height) // 2
                
                print(f"DEBUG ZOOM: new_base_sprite=({new_base_sprite_x},{new_base_sprite_y}) new_display_size=({new_display_width},{new_display_height})")
                
                # Calculate where the same sprite pixel would be with new zoom at center
                center_x_in_drawing = DRAWING_AREA_WIDTH // 2
                center_y_in_drawing = DRAWING_AREA_HEIGHT // 2
                
                # Where we want the targeted pixel to be (center of drawing area)
                target_x_at_center = new_base_sprite_x + sprite_pixel_x * new_pixeloid
                target_y_at_center = new_base_sprite_y + sprite_pixel_y * new_pixeloid
                
                print(f"DEBUG ZOOM: target_at_center=({target_x_at_center:.1f},{target_y_at_center:.1f})")
                print(f"DEBUG ZOOM: drawing_center=({center_x_in_drawing},{center_y_in_drawing})")
                
                # Calculate pan adjustment needed to center the targeted pixel
                pan_x_adjustment = center_x_in_drawing - target_x_at_center
                pan_y_adjustment = center_y_in_drawing - target_y_at_center
                
                print(f"DEBUG ZOOM: pan_adjustment=({pan_x_adjustment:.1f},{pan_y_adjustment:.1f})")
                print(f"DEBUG ZOOM: old_pan=({old_pan_x},{old_pan_y})")
                
                # Set absolute pan to center the targeted pixel (not additive)
                self.model.pan_x = int(pan_x_adjustment)
                self.model.pan_y = int(pan_y_adjustment)
                
                print(f"DEBUG ZOOM: new_pan=({self.model.pan_x},{self.model.pan_y})")
                
                # Calculate final sprite position
                final_sprite_x = new_base_sprite_x + self.model.pan_x
                final_sprite_y = new_base_sprite_y + self.model.pan_y
                
                # Calculate where targeted pixel actually ends up
                final_target_x = final_sprite_x + sprite_pixel_x * new_pixeloid
                final_target_y = final_sprite_y + sprite_pixel_y * new_pixeloid
                
                print(f"DEBUG ZOOM: final_sprite_pos=({final_sprite_x},{final_sprite_y})")
                print(f"DEBUG ZOOM: final_target_pos=({final_target_x:.1f},{final_target_y:.1f})")
                print(f"DEBUG ZOOM: center_error=({final_target_x - center_x_in_drawing:.1f},{final_target_y - center_y_in_drawing:.1f})")
                
                # Note: Skip pan constraints during zoom-to-center operations
                # to allow the image to move freely to center the targeted pixel
                
                # Update UI and clear cache
                self.view_controls_panel.components['pixeloid_label'].set_text(f'Pixeloid: {self.model.pixeloid_multiplier}x')
                self.renderer._clear_sprite_display_cache()
    
    def handle_mouse_motion(self, event):
        """Handle mouse motion to track pixeloid position"""
        self.mouse_x = event.pos[0]
        self.mouse_y = event.pos[1]
        
        # Check if mouse is in drawing area
        drawing_area = pygame.Rect(LEFT_PANEL_WIDTH, 0, DRAWING_AREA_WIDTH, DRAWING_AREA_HEIGHT)
        self.mouse_in_drawing_area = drawing_area.collidepoint(self.mouse_x, self.mouse_y)
        
        if self.mouse_in_drawing_area and self.model:
            current_sprite = self.model.get_current_sprite()
            if current_sprite:
                # Convert mouse position to drawing area coordinates
                mouse_x_in_drawing = self.mouse_x - LEFT_PANEL_WIDTH
                mouse_y_in_drawing = self.mouse_y
                
                # Calculate sprite positioning
                sprite_rect = pygame.Rect(0, 0, current_sprite.original_size[0], current_sprite.original_size[1])
                display_width = sprite_rect.width * self.model.pixeloid_multiplier
                display_height = sprite_rect.height * self.model.pixeloid_multiplier
                base_sprite_x = (DRAWING_AREA_WIDTH - display_width) // 2
                base_sprite_y = (DRAWING_AREA_HEIGHT - display_height) // 2
                sprite_x = base_sprite_x + self.model.pan_x
                sprite_y = base_sprite_y + self.model.pan_y
                
                # Calculate which sprite pixel is under the mouse
                self.sprite_pixel_x = (mouse_x_in_drawing - sprite_x) / self.model.pixeloid_multiplier
                self.sprite_pixel_y = (mouse_y_in_drawing - sprite_y) / self.model.pixeloid_multiplier
                
                # Clamp to sprite bounds
                self.sprite_pixel_x = max(0, min(current_sprite.original_size[0] - 1, self.sprite_pixel_x))
                self.sprite_pixel_y = max(0, min(current_sprite.original_size[1] - 1, self.sprite_pixel_y))
    
    def update_panning(self):
        """Update panning based on currently pressed keys"""
        if not self.model or not self.analyzer:
            return
            
        # Pan speed - scale with pixeloid multiplier for responsive movement
        base_pan_speed = 5
        pan_speed = base_pan_speed * self.model.pixeloid_multiplier
        
        # WASD movement
        if pygame.K_w in self.keys_pressed:
            self.model.pan_y += pan_speed
        if pygame.K_s in self.keys_pressed:
            self.model.pan_y -= pan_speed
        if pygame.K_a in self.keys_pressed:
            self.model.pan_x += pan_speed
        if pygame.K_d in self.keys_pressed:
            self.model.pan_x -= pan_speed
        
        # Constrain panning to reasonable bounds
        current_sprite = self.model.get_current_sprite()
        if current_sprite:
            display_width = current_sprite.original_size[0] * self.model.pixeloid_multiplier
            display_height = current_sprite.original_size[1] * self.model.pixeloid_multiplier
            
            max_pan_x = max(0, (display_width - DRAWING_AREA_WIDTH) // 2 + 200)
            max_pan_y = max(0, (display_height - DRAWING_AREA_HEIGHT) // 2 + 200)
            
            self.model.pan_x = max(-max_pan_x, min(max_pan_x, self.model.pan_x))
            self.model.pan_y = max(-max_pan_y, min(max_pan_y, self.model.pan_y))
    
    def save_analysis_data(self):
        """Save the current analysis data to JSON"""
        if not self.model:
            print("No model to save")
            return
        
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            
            # Create default filename
            sprite_name = Path(self.model.image_path).stem
            default_name = f"{sprite_name}_analysis.json"
            
            file_path = filedialog.asksaveasfilename(
                initialdir=DEFAULT_SAVE_DIR,
                initialfile=default_name,
                title="Save Analysis Data",
                filetypes=[("JSON files", "*.json")]
            )
            root.destroy()
            
            if file_path:
                self.model.save_to_json(file_path)
                print(f"Analysis data saved to: {file_path}")
                
        except Exception as e:
            print(f"Error saving analysis data: {e}")
    
    def load_analysis_data(self):
        """Load analysis data from JSON"""
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            
            file_path = filedialog.askopenfilename(
                initialdir=DEFAULT_SAVE_DIR,
                title="Load Analysis Data",
                filetypes=[("JSON files", "*.json")]
            )
            root.destroy()
            
            if file_path:
                # Load the model
                self.model = SpritesheetModel.load_from_json(file_path)
                
                # Try to load the original image
                if os.path.exists(self.model.image_path):
                    self.load_spritesheet(self.model.image_path)
                    self.analyzer = SpriteAnalyzer(self.model)
                    if self.spritesheet_surface:  # Fix Pylance warning
                        self.analyzer.load_spritesheet_surface(self.spritesheet_surface)
                else:
                    print(f"Warning: Original image not found at {self.model.image_path}")
                    print("Please load the spritesheet manually")
                
                # Update UI controls
                self.file_ops_panel.components['rows_input'].set_text(str(self.model.rows))
                self.file_ops_panel.components['cols_input'].set_text(str(self.model.cols))
                self.analysis_controls_panel.components['threshold_slider'].set_current_value(self.model.alpha_threshold)
                self.analysis_controls_panel.components['global_z_input'].set_text(str(self.model.upper_z_offset))
                
                self.update_sprite_info()
                print(f"Analysis data loaded from: {file_path}")
                
        except Exception as e:
            print(f"Error loading analysis data: {e}")


if __name__ == "__main__":
    app = AdvancedSpritesheetUI()
    app.run()
