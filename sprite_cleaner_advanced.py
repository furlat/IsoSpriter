import pygame
import pygame_gui
import os
import sys
import json
from typing import List, Tuple, Optional
from pathlib import Path

from spritesheet_model import SpritesheetModel, SpriteData, Point
from sprite_analysis import SpriteAnalyzer

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
            if ui_instance and hasattr(ui_instance, 'manual_vertices') and hasattr(ui_instance.model, 'current_sprite_index'):
                sprite_key = ui_instance.model.current_sprite_index
                manual_overrides = ui_instance.manual_vertices.get(sprite_key, {})
            
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
    """Advanced UI with two sidebars and modular components"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Advanced Spritesheet Alpha Analyzer")
        
        self.clock = pygame.time.Clock()
        self.manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Core components
        self.model: Optional[SpritesheetModel] = None
        self.analyzer: Optional[SpriteAnalyzer] = None
        self.spritesheet_surface: Optional[pygame.Surface] = None
        
        # UI state
        self.keys_pressed = set()
        
        # Mouse position tracking for pixeloid display
        self.mouse_x = 0
        self.mouse_y = 0
        self.sprite_pixel_x = 0
        self.sprite_pixel_y = 0
        self.mouse_in_drawing_area = False
        
        # Manual vertex editing mode state
        self.manual_vertex_mode = False
        self.selected_vertex = 1  # 1=N, 2=S, 3=E, 4=W
        self.selected_diamond = 'lower'  # 'lower' or 'upper'
        self.manual_vertices = {}  # Dictionary to store manual vertex overrides per sprite
        
        # Diamond visualization modes
        self.show_diamond_lines = False  # Show blue diamond outline
        self.show_raycast_analysis = True  # Show raycast lines and points
        
        # Rendering cache for draw_sprite_display computations
        self._sprite_display_cache = {}
        self._cache_size_limit = 50  # Limit cache size to prevent memory issues
        
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
            self._clear_sprite_display_cache()
            
            # Reset manual vertex state for new image
            self.manual_vertices = {}
            self.manual_vertex_mode = False
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
            self._clear_sprite_display_cache()
            
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
                self._clear_sprite_cache(self.model.current_sprite_index)
                self.update_sprite_info()
            except ValueError:
                pass  # Ignore invalid input
    
    def _clear_sprite_display_cache(self):
        """Clear the entire sprite display cache"""
        self._sprite_display_cache.clear()
    
    def _clear_sprite_cache(self, sprite_index: int):
        """Clear cache entries for a specific sprite"""
        keys_to_remove = [key for key in self._sprite_display_cache.keys() if key[0] == sprite_index]
        for key in keys_to_remove:
            del self._sprite_display_cache[key]
    
    def _get_cache_key(self, sprite_index: int, pixeloid_mult: int, alpha_threshold: int,
                       show_overlay: bool, show_diamond: bool, upper_lines_mode: bool,
                       show_diamond_vertices: bool, effective_upper_z: int, pan_x: int, pan_y: int) -> tuple:
        """Generate a cache key for the sprite display parameters"""
        # Include manual vertex mode and manual vertex data in cache key
        manual_vertices_key = None
        if self.manual_vertex_mode and sprite_index in self.manual_vertices:
            # Convert manual vertices dict to fully hashable tuple
            manual_data = self.manual_vertices[sprite_index]
            if manual_data:
                # Convert nested dicts to tuples: {'lower': {'north': (x,y)}} -> (('lower', (('north', (x,y)),)),)
                manual_vertices_key = tuple(
                    (diamond, tuple(sorted(vertices.items())))
                    for diamond, vertices in sorted(manual_data.items())
                )
        
        return (sprite_index, pixeloid_mult, alpha_threshold, show_overlay,
                show_diamond, upper_lines_mode, show_diamond_vertices, effective_upper_z,
                pan_x, pan_y, self.manual_vertex_mode, manual_vertices_key,
                self.show_diamond_lines, self.show_raycast_analysis)
    
    def _limit_cache_size(self):
        """Remove oldest cache entries if cache size exceeds limit"""
        if len(self._sprite_display_cache) > self._cache_size_limit:
            # Remove oldest entries (simple FIFO approach)
            keys_to_remove = list(self._sprite_display_cache.keys())[:-self._cache_size_limit]
            for key in keys_to_remove:
                del self._sprite_display_cache[key]
    
    
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
                    if self.manual_vertex_mode:
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
            
            self.draw_sprite_display()
            self.draw_mouse_position_display()
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
            self._clear_sprite_display_cache()
            self.update_sprite_info()
    
    def handle_global_z_change(self, text: str):
        """Handle global Z offset change"""
        if self.model:
            try:
                new_value = int(text) if text else 0
                upper_z_offset = max(0, new_value)
                self.model.update_analysis_settings(upper_z_offset=upper_z_offset)
                # Clear cache since Z offset affects analysis and rendering
                self._clear_sprite_display_cache()
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
            self._clear_sprite_display_cache()
    
    def handle_toggle_diamond_height(self):
        """Handle diamond height toggle"""
        if self.model:
            self.model.show_diamond_height = not self.model.show_diamond_height
            self.analysis_controls_panel.components['diamond_height_button'].set_text(
                f'Diamond Height: {"ON" if self.model.show_diamond_height else "OFF"}'
            )
            # Clear cache since diamond height toggle affects rendering
            self._clear_sprite_display_cache()
    
    def handle_toggle_upper_lines_mode(self):
        """Handle upper lines mode toggle"""
        if self.model:
            self.model.upper_lines_midpoint_mode = not self.model.upper_lines_midpoint_mode
            mode_text = "Midpoint" if self.model.upper_lines_midpoint_mode else "Contact Points"
            self.analysis_controls_panel.components['upper_lines_mode_button'].set_text(f'Upper Lines: {mode_text}')
            # Use the proper update method to clear analysis data
            self.model.update_analysis_settings(upper_lines_midpoint_mode=self.model.upper_lines_midpoint_mode)
            # Clear cache since upper lines mode affects rendering
            self._clear_sprite_display_cache()
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
            self._clear_sprite_display_cache()
    
    def handle_toggle_diamond_lines(self):
        """Handle diamond lines toggle"""
        self.show_diamond_lines = not self.show_diamond_lines
        self.analysis_controls_panel.components['diamond_lines_button'].set_text(
            f'Diamond Lines: {"ON" if self.show_diamond_lines else "OFF"}'
        )
        
        print(f"Diamond Lines: {'ON' if self.show_diamond_lines else 'OFF'}")
        
        # Clear cache since diamond lines toggle affects rendering
        self._clear_sprite_display_cache()
    
    def handle_toggle_raycast_analysis(self):
        """Handle raycast analysis toggle"""
        self.show_raycast_analysis = not self.show_raycast_analysis
        self.analysis_controls_panel.components['raycast_analysis_button'].set_text(
            f'Raycast Analysis: {"ON" if self.show_raycast_analysis else "OFF"}'
        )
        
        print(f"Raycast Analysis: {'ON' if self.show_raycast_analysis else 'OFF'}")
        
        # Clear cache since raycast analysis toggle affects rendering
        self._clear_sprite_display_cache()
    
    def handle_toggle_manual_vertex_mode(self):
        """Handle manual vertex mode toggle"""
        if not self.model:
            print("Please load a spritesheet first before using manual vertex mode")
            return
        
        self.manual_vertex_mode = not self.manual_vertex_mode
        self.analysis_controls_panel.components['manual_vertex_button'].set_text(
            f'Manual Vertex Mode: {"ON" if self.manual_vertex_mode else "OFF"}'
        )
        
        # Show/hide vertex selection info and auto-populate button
        self.analysis_controls_panel.components['vertex_info_label'].visible = self.manual_vertex_mode
        self.analysis_controls_panel.components['auto_populate_button'].visible = self.manual_vertex_mode
        
        if self.manual_vertex_mode:
            # Auto-enable diamond vertices display when entering manual mode
            if not self.model.show_diamond_vertices:
                self.model.show_diamond_vertices = True
                self.analysis_controls_panel.components['diamond_vertices_button'].set_text('Diamond Vertices: ON')
            
            # Update info label
            self._update_vertex_info_label()
            print(f"\n=== MANUAL VERTEX MODE: ON ===")
            print(f"Selected: {self.selected_diamond.title()} {self._get_vertex_name(self.selected_vertex)}")
            print("Controls: 1=N, 2=S, 3=E, 4=W, F1=Lower, F2=Upper, Right-click to position")
            print("Auto-Populate: Fill missing vertices from manual ones")
        else:
            print("=== MANUAL VERTEX MODE: OFF ===")
        
        # Force complete cache clear and immediate update when entering manual mode
        self._clear_sprite_display_cache()
        
        # Also update sprite info to force fresh render
        if self.manual_vertex_mode:
            self.update_sprite_info()
    
    def _get_vertex_name(self, vertex_num):
        """Get vertex name from number"""
        names = {1: 'North', 2: 'South', 3: 'East', 4: 'West'}
        return names.get(vertex_num, 'Unknown')
    
    def _update_vertex_info_label(self):
        """Update the vertex selection info label"""
        if hasattr(self.analysis_controls_panel.components, 'vertex_info_label'):
            vertex_name = self._get_vertex_name(self.selected_vertex)
            diamond_name = self.selected_diamond.title()
            info_text = f'Selected: {diamond_name} {vertex_name} ({self.selected_vertex})\n'
            info_text += 'Keys: 1234=NSEW F1/F2=Lower/Upper\n'
            info_text += 'Right-click to position'
            self.analysis_controls_panel.components['vertex_info_label'].set_text(info_text)
    
    def handle_manual_vertex_keys(self, key):
        """Handle keyboard input for manual vertex mode"""
        if not self.manual_vertex_mode:
            return
        
        # Number keys 1-4 for vertex selection (N, S, E, W)
        if key == pygame.K_1:
            self.selected_vertex = 1  # North
        elif key == pygame.K_2:
            self.selected_vertex = 2  # South
        elif key == pygame.K_3:
            self.selected_vertex = 3  # East
        elif key == pygame.K_4:
            self.selected_vertex = 4  # West
        # F1/F2 for diamond selection
        elif key == pygame.K_F1:
            self.selected_diamond = 'lower'
        elif key == pygame.K_F2:
            self.selected_diamond = 'upper'
        else:
            return  # Key not handled
        
        # Update UI and clear cache
        self._update_vertex_info_label()
        vertex_name = self._get_vertex_name(self.selected_vertex)
        print(f"Selected: {self.selected_diamond.title()} {vertex_name} ({self.selected_vertex})")
        self._clear_sprite_display_cache()
    
    def handle_right_click(self, event):
        """Handle right-click for manual vertex positioning"""
        if not self.manual_vertex_mode or not self.model:
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
        if sprite_key not in self.manual_vertices:
            self.manual_vertices[sprite_key] = {}
        
        if self.selected_diamond not in self.manual_vertices[sprite_key]:
            self.manual_vertices[sprite_key][self.selected_diamond] = {}
        
        vertex_name = self._get_vertex_name(self.selected_vertex).lower()
        self.manual_vertices[sprite_key][self.selected_diamond][vertex_name] = (original_x, original_y)
        
        # Log the positioning
        print(f"Positioned {self.selected_diamond} {vertex_name} at ({original_x}, {original_y}) "
              f"[sprite pixel: ({sprite_pixel_x:.1f}, {sprite_pixel_y:.1f})]")
        print(f"DEBUG STORAGE: manual_vertices after positioning = {self.manual_vertices}")
        
        # Clear cache to trigger re-render with new vertex position
        self._clear_sprite_display_cache()
        
        # Update measurements display to show new manual coordinates
        self.update_sprite_info()
    
    def handle_auto_populate_vertices(self):
        """Auto-populate missing vertices based on manual inputs and geometric relationships"""
        if not self.model or not self.manual_vertex_mode:
            print("Auto-populate requires manual vertex mode to be enabled")
            return
        
        sprite_key = self.model.current_sprite_index
        current_sprite = self.model.get_current_sprite()
        if not current_sprite or not current_sprite.bbox:
            print("No sprite data available for auto-populate")
            return
        
        manual_data = self.manual_vertices.get(sprite_key, {})
        if not manual_data:
            print("No manual vertices to work with")
            return
        
        bbox = current_sprite.bbox
        width = bbox.width
        
        print(f"\n=== AUTO-POPULATE VERTICES ===")
        print(f"Starting with: {manual_data}")
        
        # Initialize if needed
        if sprite_key not in self.manual_vertices:
            self.manual_vertices[sprite_key] = {}
        
        # Step 1: Complete each diamond that has >= 2 points
        for diamond_level in ['lower', 'upper']:
            diamond_data = manual_data.get(diamond_level, {})
            point_count = len(diamond_data)
            
            if point_count >= 2:
                print(f"Completing {diamond_level} diamond ({point_count} points)")
                completed_diamond = self._complete_diamond_from_points(diamond_data, width)
                
                # Update manual vertices with completed diamond
                if diamond_level not in self.manual_vertices[sprite_key]:
                    self.manual_vertices[sprite_key][diamond_level] = {}
                self.manual_vertices[sprite_key][diamond_level].update(completed_diamond)
        
        # Step 2: Handle cross-diamond derivation if needed
        lower_data = self.manual_vertices[sprite_key].get('lower', {})
        upper_data = self.manual_vertices[sprite_key].get('upper', {})
        
        lower_complete = len(lower_data) >= 4
        upper_complete = len(upper_data) >= 4
        
        if lower_complete and not upper_complete and len(upper_data) >= 1:
            # Derive z_lower from one upper point and complete upper diamond
            z_lower = self._derive_z_lower_from_diamonds(lower_data, upper_data)
            print(f"Derived z_lower: {z_lower}")
            completed_upper = self._derive_diamond_from_other(lower_data, -z_lower)  # Upper is ABOVE lower (smaller Y)
            
            if 'upper' not in self.manual_vertices[sprite_key]:
                self.manual_vertices[sprite_key]['upper'] = {}
            self.manual_vertices[sprite_key]['upper'].update(completed_upper)
            
        elif upper_complete and not lower_complete and len(lower_data) >= 1:
            # Derive z_lower from one lower point and complete lower diamond
            z_lower = self._derive_z_lower_from_diamonds(upper_data, lower_data)
            print(f"Derived z_lower: {z_lower}")
            completed_lower = self._derive_diamond_from_other(upper_data, z_lower)  # Lower is BELOW upper (larger Y)
            
            if 'lower' not in self.manual_vertices[sprite_key]:
                self.manual_vertices[sprite_key]['lower'] = {}
            self.manual_vertices[sprite_key]['lower'].update(completed_lower)
            
        elif lower_complete and not upper_complete:
            # Use algorithmic z_lower to create upper diamond
            if current_sprite.diamond_info:
                z_lower = current_sprite.diamond_info.lower_z_offset
                print(f"Using algorithmic z_lower: {z_lower}")
                completed_upper = self._derive_diamond_from_other(lower_data, -z_lower)  # Upper is ABOVE lower
                
                if 'upper' not in self.manual_vertices[sprite_key]:
                    self.manual_vertices[sprite_key]['upper'] = {}
                self.manual_vertices[sprite_key]['upper'].update(completed_upper)
                
        elif upper_complete and not lower_complete:
            # Use algorithmic z_lower to create lower diamond
            if current_sprite.diamond_info:
                z_lower = current_sprite.diamond_info.lower_z_offset
                print(f"Using algorithmic z_lower: {z_lower}")
                completed_lower = self._derive_diamond_from_other(upper_data, z_lower)  # Lower is BELOW upper
                
                if 'lower' not in self.manual_vertices[sprite_key]:
                    self.manual_vertices[sprite_key]['lower'] = {}
                self.manual_vertices[sprite_key]['lower'].update(completed_lower)
        
        print(f"Final result: {self.manual_vertices[sprite_key]}")
        
        # Clear cache and update display
        self._clear_sprite_display_cache()
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
            self._clear_sprite_display_cache()
    
    def handle_pixeloid_down(self):
        """Handle pixeloid decrease"""
        if self.model:
            self.model.pixeloid_multiplier = max(1, self.model.pixeloid_multiplier // 2)
            self.view_controls_panel.components['pixeloid_label'].set_text(f'Pixeloid: {self.model.pixeloid_multiplier}x')
            # Clear cache since pixeloid affects rendering
            self._clear_sprite_display_cache()
    
    def handle_reset_view(self):
        """Handle view reset"""
        if self.model:
            self.model.pixeloid_multiplier = 1
            self.model.pan_x = 0
            self.model.pan_y = 0
            self.view_controls_panel.components['pixeloid_label'].set_text(f'Pixeloid: {self.model.pixeloid_multiplier}x')
            # Clear cache since pixeloid and pan affects rendering
            self._clear_sprite_display_cache()
    
    def handle_center_view(self):
        """Handle view centering"""
        if self.model:
            self.model.pan_x = 0
            self.model.pan_y = 0
            # Clear cache since pan affects rendering
            self._clear_sprite_display_cache()
    
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
                self._clear_sprite_display_cache()
    
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
    
    def draw_sprite_display(self):
        """Draw the current sprite with pixeloid rendering in the center area (cached)"""
        if not self.model or not self.analyzer:
            return
        
        current_sprite = self.model.get_current_sprite()
        if not current_sprite:
            return
            
        sprite_surface = self.analyzer.get_sprite_surface(self.model.current_sprite_index)
        if not sprite_surface:
            return
        
        sprite_rect = sprite_surface.get_rect()
        if sprite_rect.width <= 0 or sprite_rect.height <= 0:
            return
        
        # Generate cache key for current rendering parameters
        effective_upper_z = self.model.get_effective_upper_z_offset(self.model.current_sprite_index)
        cache_key = self._get_cache_key(
            self.model.current_sprite_index,
            self.model.pixeloid_multiplier,
            self.model.alpha_threshold,
            self.model.show_overlay,
            self.model.show_diamond_height,
            self.model.upper_lines_midpoint_mode,
            self.model.show_diamond_vertices,
            effective_upper_z,
            self.model.pan_x,
            self.model.pan_y
        )
        
        # Check if we have a cached surface for these parameters
        if cache_key in self._sprite_display_cache:
            cached_surface, cached_clip_rect = self._sprite_display_cache[cache_key]
            # Blit the cached surface to the screen
            self.screen.set_clip(cached_clip_rect)
            self.screen.blit(cached_surface, (LEFT_PANEL_WIDTH, 0))
            self.screen.set_clip(None)
        else:
            # Create a new surface to render to for caching
            cache_surface = pygame.Surface((DRAWING_AREA_WIDTH, DRAWING_AREA_HEIGHT))
            cache_surface.fill((40, 40, 40))  # Match background color
            
            # Render to the cache surface using the original logic
            self._render_sprite_to_surface(cache_surface, sprite_surface, sprite_rect, current_sprite)
            
            # Calculate clipping rectangle
            drawing_x = LEFT_PANEL_WIDTH
            drawing_y = 0
            clip_rect = pygame.Rect(drawing_x, drawing_y, DRAWING_AREA_WIDTH, DRAWING_AREA_HEIGHT)
            
            # Store in cache
            self._sprite_display_cache[cache_key] = (cache_surface.copy(), clip_rect)
            self._limit_cache_size()
            
            # Blit to screen
            self.screen.set_clip(clip_rect)
            self.screen.blit(cache_surface, (LEFT_PANEL_WIDTH, 0))
            self.screen.set_clip(None)
        
        # Draw border around drawing area (not cached as it's always the same)
        pygame.draw.rect(self.screen, (100, 100, 100),
                        (LEFT_PANEL_WIDTH - 1, -1, DRAWING_AREA_WIDTH + 2, DRAWING_AREA_HEIGHT + 2), 1)
    
    def draw_mouse_position_display(self):
        """Draw the mouse position in pixeloid coordinates at the top center of screen"""
        if not self.model or not self.mouse_in_drawing_area:
            return
        
        # Initialize pygame font if not already done
        if not hasattr(self, '_font'):
            pygame.font.init()
            self._font = pygame.font.Font(None, 24)  # Default font, size 24
        
        # Format the pixeloid position text
        pixel_x_int = int(self.sprite_pixel_x)
        pixel_y_int = int(self.sprite_pixel_y)
        position_text = f"Pixeloid Position: ({pixel_x_int}, {pixel_y_int})"
        
        # Render the text
        text_surface = self._font.render(position_text, True, (255, 255, 255))  # White text
        text_rect = text_surface.get_rect()
        
        # Position at top center of screen
        text_x = (WINDOW_WIDTH - text_rect.width) // 2
        text_y = 10  # 10 pixels from top
        
        # Draw background rectangle for better visibility
        background_rect = pygame.Rect(text_x - 5, text_y - 2, text_rect.width + 10, text_rect.height + 4)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), background_rect)  # Semi-transparent black background
        pygame.draw.rect(self.screen, (100, 100, 100), background_rect, 1)  # Gray border
        
        # Draw the text
        self.screen.blit(text_surface, (text_x, text_y))
    
    def _render_sprite_to_surface(self, surface: pygame.Surface, sprite_surface: pygame.Surface,
                                 sprite_rect: pygame.Rect, current_sprite):
        """Render sprite content to the given surface (used for caching)"""
        if not self.model:
            return
        
        # Calculate sprite display size using pixeloid multiplier
        display_width = sprite_rect.width * self.model.pixeloid_multiplier
        display_height = sprite_rect.height * self.model.pixeloid_multiplier
        
        # Center the sprite in the surface, apply panning
        base_sprite_x = (DRAWING_AREA_WIDTH - display_width) // 2
        base_sprite_y = (DRAWING_AREA_HEIGHT - display_height) // 2
        sprite_x = base_sprite_x + self.model.pan_x
        sprite_y = base_sprite_y + self.model.pan_y
        
        # Calculate padding in pixeloids
        padding_pixeloids = 10 * self.model.pixeloid_multiplier
        actual_display_width = display_width + (padding_pixeloids * 2)
        actual_display_height = display_height + (padding_pixeloids * 2)
        
        # Calculate the top-left of the padded area
        padded_x = sprite_x - padding_pixeloids
        padded_y = sprite_y - padding_pixeloids
        
        # Draw checkerboard background aligned with pixeloid boundaries
        pixeloid_size = self.model.pixeloid_multiplier
        
        # Find the grid starting position that covers the padded area
        grid_start_x = sprite_x
        while grid_start_x > padded_x:
            grid_start_x -= pixeloid_size
        
        grid_start_y = sprite_y
        while grid_start_y > padded_y:
            grid_start_y -= pixeloid_size
        
        # Draw checkerboard grid
        y = grid_start_y
        row = 0
        while y < padded_y + actual_display_height:
            x = grid_start_x
            col = 0
            while x < padded_x + actual_display_width:
                # Checkerboard pattern
                color = (200, 200, 200) if (row + col) % 2 == 0 else (150, 150, 150)
                
                # Draw the checker square, clipped to visible area
                rect_x = max(x, padded_x)
                rect_y = max(y, padded_y)
                rect_w = min(x + pixeloid_size, padded_x + actual_display_width) - rect_x
                rect_h = min(y + pixeloid_size, padded_y + actual_display_height) - rect_y
                
                if rect_w > 0 and rect_h > 0 and rect_x >= 0 and rect_y >= 0 and rect_x < DRAWING_AREA_WIDTH and rect_y < DRAWING_AREA_HEIGHT:
                    pygame.draw.rect(surface, color, (rect_x, rect_y, rect_w, rect_h))
                
                x += pixeloid_size
                col += 1
            y += pixeloid_size
            row += 1
        
        # Draw sprite pixel by pixel as pixeloids
        for y in range(sprite_rect.height):
            for x in range(sprite_rect.width):
                pixel_color = sprite_surface.get_at((x, y))
                if pixel_color.a > self.model.alpha_threshold:  # Only draw visible pixels
                    pixel_x = sprite_x + x * self.model.pixeloid_multiplier
                    pixel_y = sprite_y + y * self.model.pixeloid_multiplier
                    if (pixel_x >= 0 and pixel_y >= 0 and
                        pixel_x < DRAWING_AREA_WIDTH and pixel_y < DRAWING_AREA_HEIGHT):
                        pixel_rect = pygame.Rect(
                            pixel_x, pixel_y,
                            self.model.pixeloid_multiplier,
                            self.model.pixeloid_multiplier
                        )
                        pygame.draw.rect(surface, pixel_color[:3], pixel_rect)
        
        # Draw overlay if enabled
        if self.model.show_overlay:
            # Draw overlay pixel by pixel as pixeloids
            for y in range(sprite_rect.height):
                for x in range(sprite_rect.width):
                    pixel_color = sprite_surface.get_at((x, y))
                    if pixel_color.a > self.model.alpha_threshold:
                        # Create overlay color (green to red gradient)
                        alpha_val = pixel_color.a
                        intensity = (alpha_val - self.model.alpha_threshold) / (255 - self.model.alpha_threshold) if self.model.alpha_threshold < 255 else 1
                        overlay_color = (int(255 * intensity), int(255 * (1 - intensity)), 0)
                        
                        pixel_x = sprite_x + x * self.model.pixeloid_multiplier
                        pixel_y = sprite_y + y * self.model.pixeloid_multiplier
                        if (pixel_x >= 0 and pixel_y >= 0 and
                            pixel_x < DRAWING_AREA_WIDTH and pixel_y < DRAWING_AREA_HEIGHT):
                            overlay_rect = pygame.Rect(
                                pixel_x, pixel_y,
                                self.model.pixeloid_multiplier,
                                self.model.pixeloid_multiplier
                            )
                            # Draw semi-transparent overlay
                            overlay_surface = pygame.Surface((self.model.pixeloid_multiplier, self.model.pixeloid_multiplier))
                            overlay_surface.set_alpha(128)
                            overlay_surface.fill(overlay_color)
                            surface.blit(overlay_surface, overlay_rect)
            
            # Draw bounding box and analysis if sprite has analysis data
            if current_sprite.bbox:
                bbox = current_sprite.bbox
                
                # Scale bounding box coordinates using pixeloid multiplier
                scaled_bbox = pygame.Rect(
                    bbox.x * self.model.pixeloid_multiplier,
                    bbox.y * self.model.pixeloid_multiplier,
                    bbox.width * self.model.pixeloid_multiplier,
                    bbox.height * self.model.pixeloid_multiplier
                )
                
                # Draw original sprite boundary (blue lines)
                original_width_scaled = sprite_rect.width * self.model.pixeloid_multiplier
                original_height_scaled = sprite_rect.height * self.model.pixeloid_multiplier
                
                line_width = max(1, min(self.model.pixeloid_multiplier, 8))  # Cap line width to prevent issues
                
                # Draw solid blue rectangle for original boundaries - check if any part is visible
                original_rect = pygame.Rect(sprite_x, sprite_y, original_width_scaled, original_height_scaled)
                drawing_area_rect = pygame.Rect(0, 0, DRAWING_AREA_WIDTH, DRAWING_AREA_HEIGHT)
                if original_rect.colliderect(drawing_area_rect):
                    # Clip the rectangle to the visible area
                    clipped_rect = original_rect.clip(drawing_area_rect)
                    pygame.draw.rect(surface, (0, 150, 255), clipped_rect, line_width)
                
                # Draw tight content bounding box (yellow lines)
                bbox_start_x = sprite_x + scaled_bbox.x
                bbox_start_y = sprite_y + scaled_bbox.y
                
                # Draw solid yellow rectangle for content boundaries - check if any part is visible
                bbox_rect = pygame.Rect(bbox_start_x, bbox_start_y, scaled_bbox.width, scaled_bbox.height)
                if bbox_rect.colliderect(drawing_area_rect):
                    # Clip the rectangle to the visible area
                    clipped_bbox = bbox_rect.clip(drawing_area_rect)
                    pygame.draw.rect(surface, (255, 255, 0), clipped_bbox, line_width)
                
                # Draw diamond height line if enabled
                if self.model.show_diamond_height and current_sprite.diamond_info:
                    diamond_info = current_sprite.diamond_info
                    
                    # Get effective upper Z offset for this frame
                    effective_upper_z = self.model.get_effective_upper_z_offset(self.model.current_sprite_index)
                    
                    # Draw upper Z offset line if present (cyan)
                    if effective_upper_z > 0:
                        upper_line_y_scaled = effective_upper_z * self.model.pixeloid_multiplier
                        upper_line_start_x = sprite_x + scaled_bbox.x
                        upper_line_end_x = sprite_x + scaled_bbox.x + scaled_bbox.width
                        upper_line_y_pos = sprite_y + scaled_bbox.y + upper_line_y_scaled
                        
                        # Draw horizontal line as cyan line - check if line is visible
                        if (upper_line_y_pos >= 0 and upper_line_y_pos < DRAWING_AREA_HEIGHT and
                            not (upper_line_end_x < 0 or upper_line_start_x >= DRAWING_AREA_WIDTH)):
                            # Clip line to visible area
                            clipped_start_x = max(0, upper_line_start_x)
                            clipped_end_x = min(DRAWING_AREA_WIDTH - 1, upper_line_end_x)
                            pygame.draw.line(surface, (0, 255, 255),
                                           (clipped_start_x, upper_line_y_pos), (clipped_end_x, upper_line_y_pos), line_width)
                    
                    # Draw the diamond height line (cyan)
                    if diamond_info.line_y and diamond_info.line_y >= bbox.y and diamond_info.line_y <= bbox.y + bbox.height:
                        # Scale the line position
                        line_y_scaled = (diamond_info.line_y - bbox.y) * self.model.pixeloid_multiplier
                        line_start_x = sprite_x + scaled_bbox.x
                        line_end_x = sprite_x + scaled_bbox.x + scaled_bbox.width
                        line_y_pos = sprite_y + scaled_bbox.y + line_y_scaled
                        
                        # Draw horizontal line as cyan line - check if line is visible
                        if (line_y_pos >= 0 and line_y_pos < DRAWING_AREA_HEIGHT and
                            not (line_end_x < 0 or line_start_x >= DRAWING_AREA_WIDTH)):
                            # Clip line to visible area
                            clipped_start_x = max(0, line_start_x)
                            clipped_end_x = min(DRAWING_AREA_WIDTH - 1, line_end_x)
                            pygame.draw.line(surface, (0, 255, 255),
                                           (clipped_start_x, line_y_pos), (clipped_end_x, line_y_pos), line_width)
                
                # Draw analysis points if available
                # Draw diamond lines if enabled (BEHIND analysis points)
                if self.show_diamond_lines and current_sprite.diamond_info:
                    pixeloid_mult = self.model.pixeloid_multiplier
                    self._draw_diamond_lines_to_surface(surface, sprite_x, sprite_y, scaled_bbox, current_sprite, pixeloid_mult)
                
                if current_sprite.detailed_analysis and self.show_raycast_analysis:
                    self._draw_analysis_points_to_surface(surface, sprite_x, sprite_y, scaled_bbox, current_sprite)

    def _draw_analysis_points_to_surface(self, surface: pygame.Surface, sprite_x, sprite_y, scaled_bbox, current_sprite):
        """Draw analysis points to the cached surface"""
        if not current_sprite.detailed_analysis or not self.model:
            return
        
        detailed_analysis = current_sprite.detailed_analysis
        pixeloid_mult = self.model.pixeloid_multiplier  # Cache for performance
        
        # Collect all occupied positions to avoid overlaps
        occupied_positions = set()
        
        # Draw convex hull areas first (GREEN) - directly from Pydantic model
        if detailed_analysis.isometric_analysis and detailed_analysis.isometric_analysis.convex_hulls:
            for direction, hull_points in detailed_analysis.isometric_analysis.convex_hulls.items():
                for hull_point in hull_points:
                    if (hull_point.x, hull_point.y) not in occupied_positions:
                        screen_x = sprite_x + scaled_bbox.x + hull_point.x * pixeloid_mult
                        screen_y = sprite_y + scaled_bbox.y + hull_point.y * pixeloid_mult
                        # Only draw if within proper bounds
                        if screen_x >= 0 and screen_x < DRAWING_AREA_WIDTH and screen_y >= 0 and screen_y < DRAWING_AREA_HEIGHT:
                            hull_surface = pygame.Surface((pixeloid_mult, pixeloid_mult))
                            hull_surface.set_alpha(100)  # Semi-transparent
                            hull_surface.fill((0, 255, 0))  # Green for all hulls
                            surface.blit(hull_surface, (screen_x, screen_y))
        
        # Draw isometric lines (PINK) - directly from Pydantic model
        if detailed_analysis.isometric_analysis and detailed_analysis.isometric_analysis.lines:
            for direction, line_points in detailed_analysis.isometric_analysis.lines.items():
                for line_point in line_points:
                    if (line_point.x, line_point.y) not in occupied_positions:
                        screen_x = sprite_x + scaled_bbox.x + line_point.x * pixeloid_mult
                        screen_y = sprite_y + scaled_bbox.y + line_point.y * pixeloid_mult
                        # Only draw if within proper bounds
                        if screen_x >= 0 and screen_x < DRAWING_AREA_WIDTH and screen_y >= 0 and screen_y < DRAWING_AREA_HEIGHT:
                            pygame.draw.rect(surface, (255, 0, 255),  # Pink for all lines
                                           (screen_x, screen_y, pixeloid_mult, pixeloid_mult))
        
        # Draw midpoints (GREEN) - directly from Pydantic model
        for midpoint_name, midpoint in detailed_analysis.midpoints.items():
            if midpoint and (midpoint.x, midpoint.y) not in occupied_positions:
                screen_x = sprite_x + scaled_bbox.x + midpoint.x * pixeloid_mult
                screen_y = sprite_y + scaled_bbox.y + midpoint.y * pixeloid_mult
                # Only draw if within proper bounds
                if screen_x >= 0 and screen_x < DRAWING_AREA_WIDTH and screen_y >= 0 and screen_y < DRAWING_AREA_HEIGHT:
                    pygame.draw.rect(surface, (0, 255, 0),
                                   (screen_x, screen_y, pixeloid_mult, pixeloid_mult))
                    occupied_positions.add((midpoint.x, midpoint.y))
        
        # Draw edge contact points (BLACK - highest priority) - directly from Pydantic model
        edge_contacts = detailed_analysis.edge_contact_points
        for contact_name in ['top_from_left', 'top_from_right', 'bottom_from_left', 'bottom_from_right',
                            'left_from_top', 'left_from_bottom', 'right_from_top', 'right_from_bottom']:
            contact_point = getattr(edge_contacts, contact_name)
            if contact_point:
                screen_x = sprite_x + scaled_bbox.x + contact_point.x * pixeloid_mult
                screen_y = sprite_y + scaled_bbox.y + contact_point.y * pixeloid_mult
                # Only draw if within proper bounds
                if screen_x >= 0 and screen_x < DRAWING_AREA_WIDTH and screen_y >= 0 and screen_y < DRAWING_AREA_HEIGHT:
                    pygame.draw.rect(surface, (0, 0, 0),
                                   (screen_x, screen_y, pixeloid_mult, pixeloid_mult))
        
        # Draw special midpoint indicators when in midpoint mode
        if self.model.upper_lines_midpoint_mode and edge_contacts.bottom_from_left and edge_contacts.bottom_from_right:
            bottom_left = edge_contacts.bottom_from_left
            bottom_right = edge_contacts.bottom_from_right
            
            effective_upper_z = self.model.get_effective_upper_z_offset(self.model.current_sprite_index)
            mid_x = (bottom_left.x + bottom_right.x) // 2
            mid_y = effective_upper_z  # Use effective upper Z offset as top edge
            
            # Draw SW starting point (left of midpoint)
            sw_x = max(0, mid_x - 1)
            screen_x_sw = sprite_x + scaled_bbox.x + sw_x * pixeloid_mult
            screen_y = sprite_y + scaled_bbox.y + mid_y * pixeloid_mult
            
            if screen_x_sw >= 0 and screen_x_sw < DRAWING_AREA_WIDTH and screen_y >= 0 and screen_y < DRAWING_AREA_HEIGHT:
                # Draw SW indicator in cyan with diagonal line
                dot_size = max(pixeloid_mult * 2, 6)
                center_x = screen_x_sw + pixeloid_mult // 2
                center_y = screen_y + pixeloid_mult // 2
                
                # Draw SW diagonal line (\)
                pygame.draw.line(surface, (0, 255, 255),
                               (center_x - dot_size//2, center_y - dot_size//2),
                               (center_x + dot_size//2, center_y + dot_size//2), 2)
            
            # Draw SE starting point (right of midpoint)
            bbox = current_sprite.bbox
            if bbox:
                se_x = min(bbox.width - 1, mid_x + 1)
                screen_x_se = sprite_x + scaled_bbox.x + se_x * pixeloid_mult
                
                if screen_x_se >= 0 and screen_x_se < DRAWING_AREA_WIDTH and screen_y >= 0 and screen_y < DRAWING_AREA_HEIGHT:
                    # Draw SE indicator in cyan with diagonal line
                    dot_size = max(pixeloid_mult * 2, 6)
                    center_x = screen_x_se + pixeloid_mult // 2
                    center_y = screen_y + pixeloid_mult // 2
                    
                    # Draw SE diagonal line (/)
                    pygame.draw.line(surface, (0, 255, 255),
                                   (center_x - dot_size//2, center_y + dot_size//2),
                                   (center_x + dot_size//2, center_y - dot_size//2), 2)
        
        # Draw diamond vertices if enabled OR if in manual vertex mode (independent of diamond lines)
        if (self.model.show_diamond_vertices or self.manual_vertex_mode) and current_sprite.diamond_info:
            self._draw_unified_diamond_vertices(surface, sprite_x, sprite_y, scaled_bbox, current_sprite, pixeloid_mult)
    
    def _draw_unified_diamond_vertices(self, surface: pygame.Surface, sprite_x, sprite_y, scaled_bbox, current_sprite, pixeloid_mult):
        """Single unified function to draw diamond vertices (both algorithmic and manual)"""
        if not current_sprite.diamond_info or not self.model:
            return
            
        diamond_info = current_sprite.diamond_info
        bbox = current_sprite.bbox
        if not bbox:
            return
            
        # Initialize font for vertex labels if not already done
        if not hasattr(self, '_vertex_font'):
            pygame.font.init()
            self._vertex_font = pygame.font.Font(None, max(12, pixeloid_mult + 2))
        
        # Get manual vertex overrides for current sprite
        sprite_key = self.model.current_sprite_index
        manual_overrides = self.manual_vertices.get(sprite_key, {})
        
        # Draw lower diamond vertices
        if diamond_info.lower_diamond:
            self._draw_diamond_level_vertices(
                surface, sprite_x, sprite_y, scaled_bbox, bbox, pixeloid_mult,
                'lower', diamond_info.lower_diamond, manual_overrides.get('lower', {}),
                False  # False = square vertices for lower
            )
        
        # Draw upper diamond vertices if present
        if diamond_info.upper_diamond:
            self._draw_diamond_level_vertices(
                surface, sprite_x, sprite_y, scaled_bbox, bbox, pixeloid_mult,
                'upper', diamond_info.upper_diamond, manual_overrides.get('upper', {}),
                True  # True = diamond vertices for upper
            )
    
    def _draw_diamond_level_vertices(self, surface, sprite_x, sprite_y, scaled_bbox, bbox, pixeloid_mult,
                                   diamond_level, diamond_data, manual_overrides, is_upper):
        """Draw vertices for a single diamond level (lower or upper)"""
        vertex_size = max(pixeloid_mult, 4)
        
        for vertex_name, vertex in [
            ('N', diamond_data.north_vertex), ('S', diamond_data.south_vertex),
            ('E', diamond_data.east_vertex), ('W', diamond_data.west_vertex)
        ]:
            # Get the coordinates to use
            coords = self._get_vertex_coords(vertex_name, vertex, manual_overrides, bbox)
            if coords is None:
                continue  # Skip if no coordinates available
                
            abs_x, abs_y, is_manual = coords
            
            # Convert to screen coordinates using the SAME logic as algorithmic
            rel_x = abs_x - bbox.x
            rel_y = abs_y - bbox.y
            screen_x = sprite_x + scaled_bbox.x + rel_x * pixeloid_mult
            screen_y = sprite_y + scaled_bbox.y + rel_y * pixeloid_mult
            
            # Check bounds
            if not (0 <= screen_x < DRAWING_AREA_WIDTH and 0 <= screen_y < DRAWING_AREA_HEIGHT):
                continue
                
            # Choose color
            vertex_color = (0, 255, 255) if is_manual else (255, 255, 255)  # Cyan for manual, white for algorithmic
            
            # Draw the vertex shape
            if is_upper:
                self._draw_diamond_shape(surface, screen_x, screen_y, vertex_size, vertex_color)
                label = f"U{vertex_name}"
            else:
                self._draw_square_shape(surface, screen_x, screen_y, vertex_size, vertex_color)
                label = vertex_name
            
            # Highlight selected vertex
            if (self.manual_vertex_mode and self.selected_diamond == diamond_level and
                self._get_vertex_name(self.selected_vertex).upper() == vertex_name):
                if is_upper:
                    self._draw_diamond_shape(surface, screen_x, screen_y, vertex_size, None, (255, 255, 0), 2)
                else:
                    self._draw_square_shape(surface, screen_x, screen_y, vertex_size, None, (255, 255, 0), 2)
            
            # Draw label
            self._draw_vertex_label(surface, label, screen_x, screen_y, vertex_size, pixeloid_mult)
    
    def _get_vertex_coords(self, vertex_name, vertex, manual_overrides, bbox):
        """Get coordinates for a vertex, choosing path based on current toggle mode"""
        manual_key_map = {'n': 'north', 's': 'south', 'e': 'east', 'w': 'west'}
        manual_key = manual_key_map[vertex_name.lower()]
        
        if self.manual_vertex_mode:
            # Manual mode: prefer manual, fallback to algorithmic
            if manual_key in manual_overrides:
                manual_x, manual_y = manual_overrides[manual_key]
                return (manual_x, manual_y, True)  # Return absolute coords + manual flag
            elif vertex:
                return (vertex.x, vertex.y, False)  # Fallback to algorithmic
            else:
                return None  # No vertex data available
        else:
            # Normal mode: use algorithmic vertices only
            if vertex:
                return (vertex.x, vertex.y, False)  # Return absolute coords + algorithmic flag
            else:
                return None  # Skip if no algorithmic vertex
    
    def _draw_square_shape(self, surface, x, y, size, fill_color=None, border_color=(0, 0, 0), border_width=1):
        """Draw a square vertex shape"""
        rect = pygame.Rect(x, y, size, size)
        if fill_color:
            pygame.draw.rect(surface, fill_color, rect)
        if border_color and border_width > 0:
            pygame.draw.rect(surface, border_color, rect, border_width)
    
    def _draw_diamond_shape(self, surface, x, y, size, fill_color=None, border_color=(0, 0, 0), border_width=1):
        """Draw a diamond vertex shape"""
        center_x = x + size // 2
        center_y = y + size // 2
        points = [
            (center_x, center_y - size // 2),  # top
            (center_x + size // 2, center_y),  # right
            (center_x, center_y + size // 2),  # bottom
            (center_x - size // 2, center_y)   # left
        ]
        if fill_color:
            pygame.draw.polygon(surface, fill_color, points)
        if border_color and border_width > 0:
            pygame.draw.polygon(surface, border_color, points, border_width)
    
    def _draw_vertex_label(self, surface: pygame.Surface, label: str, vertex_x: int, vertex_y: int,
                          vertex_size: int, pixeloid_mult: int):
        """Draw a text label next to a diamond vertex with proper positioning"""
        if not hasattr(self, '_vertex_font'):
            return
        
        # Render the text
        text_surface = self._vertex_font.render(label, True, (255, 255, 0))  # Yellow text for good visibility
        text_rect = text_surface.get_rect()
        
        # Calculate label offset based on vertex direction
        offset_distance = max(vertex_size + 2, pixeloid_mult + 4)
        
        # Position label based on cardinal direction
        if 'N' in label:  # North - above vertex
            label_x = vertex_x + vertex_size // 2 - text_rect.width // 2
            label_y = vertex_y - text_rect.height - 2
        elif 'S' in label:  # South - below vertex
            label_x = vertex_x + vertex_size // 2 - text_rect.width // 2
            label_y = vertex_y + vertex_size + 2
        elif 'E' in label:  # East - right of vertex
            label_x = vertex_x + vertex_size + 2
            label_y = vertex_y + vertex_size // 2 - text_rect.height // 2
        elif 'W' in label:  # West - left of vertex
            label_x = vertex_x - text_rect.width - 2
            label_y = vertex_y + vertex_size // 2 - text_rect.height // 2
        else:  # Default positioning (should not happen)
            label_x = vertex_x + vertex_size + 2
            label_y = vertex_y
        
        # Ensure label stays within drawing area bounds
        label_x = max(0, min(label_x, DRAWING_AREA_WIDTH - text_rect.width))
        label_y = max(0, min(label_y, DRAWING_AREA_HEIGHT - text_rect.height))
        
        # Draw background rectangle for better text visibility
        bg_rect = pygame.Rect(label_x - 1, label_y - 1, text_rect.width + 2, text_rect.height + 2)
        pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect)  # Semi-transparent black background
        pygame.draw.rect(surface, (100, 100, 100), bg_rect, 1)  # Gray border
        
        # Draw the text
        surface.blit(text_surface, (label_x, label_y))
    
    def _draw_diamond_lines_to_surface(self, surface: pygame.Surface, sprite_x, sprite_y, scaled_bbox, current_sprite, pixeloid_mult):
        """Draw blue diamond outline connecting vertices"""
        if not current_sprite.diamond_info or not self.model:
            return
            
        diamond_info = current_sprite.diamond_info
        bbox = current_sprite.bbox
        if not bbox:
            return
        
        # Get manual vertex overrides for current sprite
        sprite_key = self.model.current_sprite_index
        manual_overrides = self.manual_vertices.get(sprite_key, {})
        
        line_width = max(2, pixeloid_mult // 2)  # Scale line width with zoom
        
        # Draw lower diamond outline
        if diamond_info.lower_diamond:
            self._draw_diamond_outline(
                surface, sprite_x, sprite_y, scaled_bbox, bbox, pixeloid_mult,
                diamond_info.lower_diamond, manual_overrides.get('lower', {}),
                (255, 255, 0), line_width  # Yellow color
            )
        
        # Draw upper diamond outline if present
        if diamond_info.upper_diamond:
            self._draw_diamond_outline(
                surface, sprite_x, sprite_y, scaled_bbox, bbox, pixeloid_mult,
                diamond_info.upper_diamond, manual_overrides.get('upper', {}),
                (255, 200, 0), line_width  # Lighter yellow color
            )
    
    def _draw_diamond_outline(self, surface, sprite_x, sprite_y, scaled_bbox, bbox, pixeloid_mult,
                             diamond_data, manual_overrides, color, line_width):
        """Draw outline connecting diamond vertices using pixeloid squares"""
        # Get all vertex coordinates in bbox-relative space
        vertices = {}
        vertex_data = [
            ('N', diamond_data.north_vertex),
            ('S', diamond_data.south_vertex),
            ('E', diamond_data.east_vertex),
            ('W', diamond_data.west_vertex)
        ]
        
        for vertex_name, vertex in vertex_data:
            coords = self._get_vertex_coords(vertex_name, vertex, manual_overrides, bbox)
            if coords:
                abs_x, abs_y, _ = coords
                # Store in bbox-relative coordinates for line tracing
                rel_x = abs_x - bbox.x
                rel_y = abs_y - bbox.y
                vertices[vertex_name] = (rel_x, rel_y)
        
        # Draw diamond outline using pixeloid squares (N->E->S->W->N)
        if len(vertices) >= 4:
            # Define diamond edge connections
            edges = [('N', 'E'), ('S','E'), ('S', 'W'), ('N','W')]
            
            for start_vertex, end_vertex in edges:
                if start_vertex in vertices and end_vertex in vertices:
                    start_pos = vertices[start_vertex]
                    end_pos = vertices[end_vertex]
                    
                    # Apply directional offset based on edge direction (mimic raycast behavior)
                    offset_start_pos = self._apply_directional_offset(start_pos, start_vertex, end_vertex)
                    
                    # Trace pixeloid line between vertices
                    line_points = self._trace_pixeloid_line(offset_start_pos[0], offset_start_pos[1], end_pos[0], end_pos[1])
                    
                    # Draw each point as a pixeloid square with same offset as raycast analysis
                    for rel_x, rel_y in line_points:
                        # Apply the same coordinate system as raycast analysis (bbox-relative with proper offset)
                        screen_x = sprite_x + scaled_bbox.x + rel_x * pixeloid_mult
                        screen_y = sprite_y + scaled_bbox.y + rel_y * pixeloid_mult
                        
                        # Only draw if within drawing area bounds
                        if (screen_x >= 0 and screen_x < DRAWING_AREA_WIDTH and
                            screen_y >= 0 and screen_y < DRAWING_AREA_HEIGHT):
                            # Use blue color like requested originally
                            pygame.draw.rect(surface, color, (screen_x, screen_y, pixeloid_mult, pixeloid_mult))
    
    def _apply_directional_offset(self, start_pos, start_vertex, end_vertex):
        """Apply directional starting offset based on edge direction to mimic raycast behavior"""
        x, y = start_pos
        
        # Offset North/South vertices based on direction they're heading
        # East/West targets are hit precisely (no adjustment to targets)
        if start_vertex == 'N' and end_vertex == 'E':  # North to East (going right)
            return (x + 1, y)  # North + 1 right
        elif start_vertex == 'N' and end_vertex == 'W':  # North to West (going left)
            return (x - 1, y)  # North + 1 left
        elif start_vertex == 'S' and end_vertex == 'E':  # South to East (going right)
            return (x + 1, y)  # South + 1 right
        elif start_vertex == 'S' and end_vertex == 'W':  # South to West (going left)
            return (x - 1, y)  # South + 1 left
        else:
            return (x, y)  # East/West sources need no offset
    
    def _trace_pixeloid_line(self, start_x, start_y, end_x, end_y):
        """Trace a line between two points using pixeloid steps, stopping just before the end vertex like raycasts do"""
        points = []
        
        # Convert to integers for pixel-perfect tracing
        x0, y0 = int(start_x), int(start_y)
        x1, y1 = int(end_x), int(end_y)
        
        # Calculate direction and length
        dx_total = x1 - x0
        dy_total = y1 - y0
        length = max(abs(dx_total), abs(dy_total))
        
        if length <= 1:
            return points  # Too short to draw anything meaningful
        
        # Bresenham's line algorithm for pixeloid-perfect lines
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        
        err = dx - dy
        x, y = x0, y0
        
        # Start from the actual start vertex (like raycasts do)
        points.append((x, y))
        
        # Trace toward end vertex but stop before reaching it
        while True:
            e2 = 2 * err
            
            if e2 > -dy:
                err -= dy
                x += sx
                
            if e2 < dx:
                err += dx
                y += sy
            
            # Stop one step before reaching the end vertex (like raycasts stop at boundaries)
            next_x = x
            next_y = y
            if e2 > -dy:
                next_x = x + sx if x != x1 else x
            if e2 < dx:
                next_y = y + sy if y != y1 else y
                
            # If the next step would reach the end vertex, stop here
            if next_x == x1 and next_y == y1:
                break
                
            # If we've reached the end vertex, stop
            if x == x1 and y == y1:
                break
                
            points.append((x, y))
        
        return points

    def draw_analysis_points(self, sprite_x, sprite_y, scaled_bbox, current_sprite):
        """Draw analysis points (contact points, midpoints, isometric lines, convex hulls)"""
        if not current_sprite.detailed_analysis or not self.model:
            return
        
        detailed_analysis = current_sprite.detailed_analysis
        pixeloid_mult = self.model.pixeloid_multiplier  # Cache for performance
        
        # Collect all occupied positions to avoid overlaps
        occupied_positions = set()
        
        # Draw convex hull areas first (GREEN) - directly from Pydantic model
        if detailed_analysis.isometric_analysis and detailed_analysis.isometric_analysis.convex_hulls:
            for direction, hull_points in detailed_analysis.isometric_analysis.convex_hulls.items():
                for hull_point in hull_points:
                    if (hull_point.x, hull_point.y) not in occupied_positions:
                        screen_x = sprite_x + scaled_bbox.x + hull_point.x * pixeloid_mult
                        screen_y = sprite_y + scaled_bbox.y + hull_point.y * pixeloid_mult
                        # Only draw if within proper bounds (not over sidebars)
                        if screen_x >= LEFT_PANEL_WIDTH and screen_x < LEFT_PANEL_WIDTH + DRAWING_AREA_WIDTH:
                            hull_surface = pygame.Surface((pixeloid_mult, pixeloid_mult))
                            hull_surface.set_alpha(100)  # Semi-transparent
                            hull_surface.fill((0, 255, 0))  # Green for all hulls
                            self.screen.blit(hull_surface, (screen_x, screen_y))
        
        # Draw isometric lines (PINK) - directly from Pydantic model
        if detailed_analysis.isometric_analysis and detailed_analysis.isometric_analysis.lines:
            for direction, line_points in detailed_analysis.isometric_analysis.lines.items():
                for line_point in line_points:
                    if (line_point.x, line_point.y) not in occupied_positions:
                        screen_x = sprite_x + scaled_bbox.x + line_point.x * pixeloid_mult
                        screen_y = sprite_y + scaled_bbox.y + line_point.y * pixeloid_mult
                        # Only draw if within proper bounds (not over sidebars)
                        if screen_x >= LEFT_PANEL_WIDTH and screen_x < LEFT_PANEL_WIDTH + DRAWING_AREA_WIDTH:
                            pygame.draw.rect(self.screen, (255, 0, 255),  # Pink for all lines
                                           (screen_x, screen_y, pixeloid_mult, pixeloid_mult))
        
        # Draw midpoints (GREEN) - directly from Pydantic model
        for midpoint_name, midpoint in detailed_analysis.midpoints.items():
            if midpoint and (midpoint.x, midpoint.y) not in occupied_positions:
                screen_x = sprite_x + scaled_bbox.x + midpoint.x * pixeloid_mult
                screen_y = sprite_y + scaled_bbox.y + midpoint.y * pixeloid_mult
                # Only draw if within proper bounds (not over sidebars)
                if screen_x >= LEFT_PANEL_WIDTH and screen_x < LEFT_PANEL_WIDTH + DRAWING_AREA_WIDTH:
                    pygame.draw.rect(self.screen, (0, 255, 0),
                                   (screen_x, screen_y, pixeloid_mult, pixeloid_mult))
                    occupied_positions.add((midpoint.x, midpoint.y))
        
        # Draw edge contact points (BLACK - highest priority) - directly from Pydantic model
        edge_contacts = detailed_analysis.edge_contact_points
        for contact_name in ['top_from_left', 'top_from_right', 'bottom_from_left', 'bottom_from_right',
                            'left_from_top', 'left_from_bottom', 'right_from_top', 'right_from_bottom']:
            contact_point = getattr(edge_contacts, contact_name)
            if contact_point:
                screen_x = sprite_x + scaled_bbox.x + contact_point.x * pixeloid_mult
                screen_y = sprite_y + scaled_bbox.y + contact_point.y * pixeloid_mult
                # Only draw if within proper bounds (not over sidebars)
                if screen_x >= LEFT_PANEL_WIDTH and screen_x < LEFT_PANEL_WIDTH + DRAWING_AREA_WIDTH:
                    pygame.draw.rect(self.screen, (0, 0, 0),
                                   (screen_x, screen_y, pixeloid_mult, pixeloid_mult))
        
        # Draw special midpoint indicators when in midpoint mode
        if self.model.upper_lines_midpoint_mode and edge_contacts.bottom_from_left and edge_contacts.bottom_from_right:
            bottom_left = edge_contacts.bottom_from_left
            bottom_right = edge_contacts.bottom_from_right
            
            effective_upper_z = self.model.get_effective_upper_z_offset(self.model.current_sprite_index)
            mid_x = (bottom_left.x + bottom_right.x) // 2
            mid_y = effective_upper_z  # Use effective upper Z offset as top edge
            
            # Draw SW starting point (left of midpoint)
            sw_x = max(0, mid_x - 1)
            screen_x_sw = sprite_x + scaled_bbox.x + sw_x * pixeloid_mult
            screen_y = sprite_y + scaled_bbox.y + mid_y * pixeloid_mult
            
            if screen_x_sw >= LEFT_PANEL_WIDTH and screen_x_sw < LEFT_PANEL_WIDTH + DRAWING_AREA_WIDTH:
                # Draw SW indicator in cyan with diagonal line
                dot_size = max(pixeloid_mult * 2, 6)
                center_x = screen_x_sw + pixeloid_mult // 2
                center_y = screen_y + pixeloid_mult // 2
                
                # Draw SW diagonal line (\)
                pygame.draw.line(self.screen, (0, 255, 255),
                               (center_x - dot_size//2, center_y - dot_size//2),
                               (center_x + dot_size//2, center_y + dot_size//2), 2)
            
            # Draw SE starting point (right of midpoint)
            bbox = current_sprite.bbox
            if bbox:
                se_x = min(bbox.width - 1, mid_x + 1)
                screen_x_se = sprite_x + scaled_bbox.x + se_x * pixeloid_mult
                
                if screen_x_se >= LEFT_PANEL_WIDTH and screen_x_se < LEFT_PANEL_WIDTH + DRAWING_AREA_WIDTH:
                    # Draw SE indicator in cyan with diagonal line
                    dot_size = max(pixeloid_mult * 2, 6)
                    center_x = screen_x_se + pixeloid_mult // 2
                    center_y = screen_y + pixeloid_mult // 2
                    
                    # Draw SE diagonal line (/)
                    pygame.draw.line(self.screen, (0, 255, 255),
                                   (center_x - dot_size//2, center_y + dot_size//2),
                                   (center_x + dot_size//2, center_y - dot_size//2), 2)
    
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