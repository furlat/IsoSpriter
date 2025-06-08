import pygame
import pygame_gui
from typing import Optional, Dict, Any
from pathlib import Path
from spritesheet_model import SpritesheetModel, SpriteData


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
        
        # Global Manual Diamond Width
        self.components['global_diamond_width_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 140, 25),
            text='Global Diamond Width:',
            manager=self.manager
        )
        self.components['global_diamond_width_input'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(self.start_x + 155, current_y, 175, 25),
            manager=self.manager
        )
        self.components['global_diamond_width_input'].set_text('')
        current_y += 35
        
        # Frame Manual Diamond Width
        self.components['frame_diamond_width_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 140, 25),
            text='Frame Diamond Width:',
            manager=self.manager
        )
        self.components['frame_diamond_width_input'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(self.start_x + 155, current_y, 175, 25),
            manager=self.manager
        )
        self.components['frame_diamond_width_input'].set_text('')
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
        
        # Delete All Custom Keypoints button (initially hidden)
        self.components['delete_keypoints_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 30),
            text='Delete All Custom Keypoints',
            manager=self.manager
        )
        self.components['delete_keypoints_button'].visible = False
        current_y += 35
        
        # Reset Manual Vertices button (initially hidden)
        self.components['reset_vertices_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 30),
            text='Reset Manual Vertices',
            manager=self.manager
        )
        self.components['reset_vertices_button'].visible = False
        current_y += 35
        
        # Manual vertex controls (initially hidden)
        self.components['vertex_info_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 50),
            text='Selected: Lower North (1)\nKeys: 1234=NSEW F1/F2=Lower/Upper\nLeft-click to position',
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