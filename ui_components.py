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
        
        self.components['sub_diamond_mode_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 30),
            text='Sub-Diamond Mode: OFF',
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
    """Component for essential view controls only"""
    
    def __init__(self, manager, start_x, start_y, panel_width):
        self.manager = manager
        self.start_x = start_x
        self.start_y = start_y
        self.panel_width = panel_width
        self.components = {}
        self.create_components()
    
    def create_components(self):
        current_y = self.start_y + 10
        
        # Essential view controls only
        self.components['pixeloid_reset_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 150, 35),
            text='Reset View',
            manager=self.manager
        )
        self.components['center_view_button'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.start_x + 170, current_y, 160, 35),
            text='Center View',
            manager=self.manager
        )
        current_y += 50
        
        self.height = current_y - self.start_y


class SubDiamondControlsPanel:
    """Component for sub-diamond editing controls and status"""
    
    def __init__(self, manager, start_x, start_y, panel_width):
        self.manager = manager
        self.start_x = start_x
        self.start_y = start_y
        self.panel_width = panel_width
        self.components = {}
        self.create_components()
    
    def create_components(self):
        current_y = self.start_y + 10
        
        # Sub-diamond mode status
        self.components['mode_status_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 25),
            text='Sub-Diamond Mode: OFF',
            manager=self.manager
        )
        current_y += 30
        
        # Current layer
        self.components['layer_status_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 25),
            text='Layer: LOWER',
            manager=self.manager
        )
        current_y += 30
        
        # Current editing mode
        self.components['editing_mode_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 25),
            text='Editing: WALKABILITY',
            manager=self.manager
        )
        current_y += 30
        
        # Instructions
        self.components['instructions_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 75),
            text='Controls:\nF1/F2: Lower/Upper Diamond\nF3: Cycle Layers\n1: Line of Sight, 2: Walkability\nLeft Click: Toggle, Right Click: None',
            manager=self.manager
        )
        current_y += 85
        
        # Color legend
        self.components['color_legend_label'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(self.start_x + 10, current_y, 320, 100),
            text='Colors:\nWalkable: Green, Not Walkable: Red\nCan See & Walk: Green\nNo See No Walk: Red\nSee No Walk: Blue\nNo See Walk: Purple\nNone: Gray',
            manager=self.manager
        )
        current_y += 110
        
        self.height = current_y - self.start_y
    
    def update_status(self, sub_diamond_mode, layer, editing_mode):
        """Update the status displays"""
        mode_text = "ON" if sub_diamond_mode else "OFF"
        self.components['mode_status_label'].set_text(f'Sub-Diamond Mode: {mode_text}')
        self.components['layer_status_label'].set_text(f'Layer: {layer.upper()}')
        self.components['editing_mode_label'].set_text(f'Editing: {editing_mode.upper().replace("_", " ")}')

