import pygame
import pygame_gui
import os
from typing import Optional, Dict, Any
from pathlib import Path
from spritesheet_model import SpritesheetModel
from sprite_analysis import SpriteAnalyzer


class InputHandlers:
    """Handles all input processing for the sprite cleaner application"""
    
    def __init__(self, ui_instance):
        """Initialize with reference to the main UI instance"""
        self.ui = ui_instance
        
        # Constants for easy access
        self.DEFAULT_SPRITESHEET_DIR = r"C:\Users\Tommaso\Documents\Dev\Spriter\tiles\isometric_tiles\blocks"
        self.DEFAULT_SAVE_DIR = r"C:\Users\Tommaso\Documents\Dev\Spriter\analysis_data"
        
        # Drawing area constants
        self.LEFT_PANEL_WIDTH = 350
        self.DRAWING_AREA_WIDTH = 1700  # 2400 - 350 - 350
        self.DRAWING_AREA_HEIGHT = 1200
    
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
        elif event.ui_element == ui_elements['analysis_sub_diamond_mode_button']:
            self.handle_toggle_sub_diamond_mode()
        elif event.ui_element == ui_elements['analysis_auto_populate_button']:
            self.handle_auto_populate_vertices()
        elif event.ui_element == ui_elements['analysis_delete_keypoints_button']:
            self.handle_delete_all_custom_keypoints()
        elif event.ui_element == ui_elements['analysis_reset_vertices_button']:
            self.handle_reset_manual_vertices()
        elif event.ui_element == ui_elements['view_pixeloid_reset_button']:
            self.handle_reset_view()
        elif event.ui_element == ui_elements['view_center_view_button']:
            self.handle_center_view()
        elif event.ui_element == ui_elements['sub_diamond_set_default_button']:
            self.handle_sub_diamond_set_default()
        elif event.ui_element == ui_elements['sub_diamond_clear_all_button']:
            self.handle_sub_diamond_clear_all()
        elif event.ui_element == ui_elements['sub_diamond_set_all_true_button']:
            self.handle_sub_diamond_set_all_true()
        elif event.ui_element == ui_elements['sub_diamond_set_all_false_button']:
            self.handle_sub_diamond_set_all_false()
        elif event.ui_element == ui_elements['sub_diamond_propagate_rotation_button']:
            self.handle_propagate_rotation()
    
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
        elif event.ui_element == ui_elements['analysis_global_diamond_width_input']:
            self.handle_global_diamond_width_change(event.text)
        elif event.ui_element == ui_elements['analysis_frame_diamond_width_input']:
            self.handle_frame_diamond_width_change(event.text)
    
    def handle_file_load(self):
        """Handle file loading"""
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            
            initial_dir = self.DEFAULT_SPRITESHEET_DIR if os.path.exists(self.DEFAULT_SPRITESHEET_DIR) else None
            
            file_path = filedialog.askopenfilename(
                initialdir=initial_dir,
                title="Select Spritesheet",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            root.destroy()
            
            if file_path:
                if self.ui.load_spritesheet(file_path):
                    self.ui.create_model_from_inputs(file_path)
                else:
                    print("Failed to load spritesheet")
        except Exception as e:
            print(f"Error opening file dialog: {e}")
    
    def handle_split_spritesheet(self):
        """Handle spritesheet splitting"""
        if self.ui.spritesheet_surface:
            image_path = self.ui.model.image_path if self.ui.model else "unknown"
            self.ui.create_model_from_inputs(image_path)
    
    def handle_prev_sprite(self):
        """Handle previous sprite navigation"""
        if self.ui.model and self.ui.model.current_sprite_index > 0:
            self.ui.model.current_sprite_index -= 1
            self.ui.model.pan_x = 0
            self.ui.model.pan_y = 0
            self.ui.update_sprite_info()
    
    def handle_next_sprite(self):
        """Handle next sprite navigation"""
        if self.ui.model and self.ui.model.current_sprite_index < len(self.ui.model.sprites) - 1:
            self.ui.model.current_sprite_index += 1
            self.ui.model.pan_x = 0
            self.ui.model.pan_y = 0
            self.ui.update_sprite_info()
    
    def handle_threshold_change(self, value: int):
        """Handle alpha threshold change"""
        if self.ui.model:
            self.ui.model.update_analysis_settings(alpha_threshold=value)
            self.ui.analysis_controls_panel.components['threshold_label'].set_text(f'Alpha Threshold: {value}')
            # Clear cache since alpha threshold affects sprite rendering
            self.ui.renderer._clear_sprite_display_cache()
            self.ui.update_sprite_info()
    
    def handle_global_z_change(self, text: str):
        """Handle global Z offset change"""
        if self.ui.model:
            try:
                new_value = int(text) if text else 0
                upper_z_offset = max(0, new_value)
                self.ui.model.update_analysis_settings(upper_z_offset=upper_z_offset)
                # Clear cache since Z offset affects analysis and rendering
                self.ui.renderer._clear_sprite_display_cache()
                self.ui.update_sprite_info()
            except ValueError:
                pass  # Ignore invalid input
    
    def handle_frame_z_offset_change(self, text: str):
        """Handle frame-specific Z offset change"""
        if self.ui.model:
            try:
                new_value = int(text) if text else 0
                frame_z_offset = max(0, new_value)
                self.ui.model.set_frame_upper_z_offset(self.ui.model.current_sprite_index, frame_z_offset)
                # Clear cache for this specific sprite since its rendering changed
                self.ui.renderer._clear_sprite_cache(self.ui.model.current_sprite_index)
                self.ui.update_sprite_info()
            except ValueError:
                pass  # Ignore invalid input
    
    def handle_global_diamond_width_change(self, text: str):
        """Handle global manual diamond width change"""
        if self.ui.model:
            try:
                new_value = int(text) if text else None
                if new_value is not None:
                    self.ui.model.manual_diamond_width = max(0, new_value) if new_value > 0 else None
                else:
                    self.ui.model.manual_diamond_width = None
                
                print(f"Global diamond width changed to: {self.ui.model.manual_diamond_width}")
                
                # Re-analyze current sprite with new effective diamond width
                self._reanalyze_current_sprite_with_new_diamond_width()
                
            except ValueError:
                pass  # Ignore invalid input
    
    def handle_frame_diamond_width_change(self, text: str):
        """Handle frame-specific manual diamond width change"""
        if self.ui.model:
            try:
                new_value = int(text) if text else None
                current_sprite = self.ui.model.get_current_sprite()
                if current_sprite:
                    if new_value is not None:
                        current_sprite.manual_diamond_width = max(0, new_value) if new_value > 0 else None
                    else:
                        current_sprite.manual_diamond_width = None
                    
                    print(f"Frame diamond width changed to: {current_sprite.manual_diamond_width}")
                    
                    # Re-analyze current sprite with new effective diamond width
                    self._reanalyze_current_sprite_with_new_diamond_width()
                    
            except ValueError:
                pass  # Ignore invalid input
    
    def _reanalyze_current_sprite_with_new_diamond_width(self):
        """Re-analyze current sprite with the new effective diamond width"""
        if not self.ui.model or not self.ui.analyzer:
            return
        
        current_sprite = self.ui.model.get_current_sprite()
        if not current_sprite:
            return
        
        print(f"Re-analyzing sprite {self.ui.model.current_sprite_index} with new diamond width...")
        
        # Get the effective diamond width for this sprite
        effective_width = self.ui.model.get_effective_diamond_width(self.ui.model.current_sprite_index)
        print(f"Effective diamond width: {effective_width}")
        
        # Trigger re-analysis of the current sprite using the new effective width
        # This will recalculate diamond vertices using the manual width
        try:
            self.ui.analyzer.analyze_sprite(self.ui.model.current_sprite_index)
            print("Sprite re-analysis completed")
            
            # Clear rendering cache and update display
            self.ui.renderer._clear_sprite_display_cache()
            self.ui.update_sprite_info()
            
        except Exception as e:
            print(f"Error during sprite re-analysis: {e}")
    
    def handle_toggle_overlay(self):
        """Handle overlay toggle"""
        if self.ui.model:
            self.ui.model.show_overlay = not self.ui.model.show_overlay
            self.ui.analysis_controls_panel.components['overlay_button'].set_text(
                f'Toggle Overlay: {"ON" if self.ui.model.show_overlay else "OFF"}'
            )
            # Clear cache since overlay toggle affects rendering
            self.ui.renderer._clear_sprite_display_cache()
    
    def handle_toggle_diamond_height(self):
        """Handle diamond height toggle"""
        if self.ui.model:
            self.ui.model.show_diamond_height = not self.ui.model.show_diamond_height
            self.ui.analysis_controls_panel.components['diamond_height_button'].set_text(
                f'Diamond Height: {"ON" if self.ui.model.show_diamond_height else "OFF"}'
            )
            # Clear cache since diamond height toggle affects rendering
            self.ui.renderer._clear_sprite_display_cache()
    
    def handle_toggle_upper_lines_mode(self):
        """Handle upper lines mode toggle"""
        if self.ui.model:
            self.ui.model.upper_lines_midpoint_mode = not self.ui.model.upper_lines_midpoint_mode
            mode_text = "Midpoint" if self.ui.model.upper_lines_midpoint_mode else "Contact Points"
            self.ui.analysis_controls_panel.components['upper_lines_mode_button'].set_text(f'Upper Lines: {mode_text}')
            # Use the proper update method to clear analysis data
            self.ui.model.update_analysis_settings(upper_lines_midpoint_mode=self.ui.model.upper_lines_midpoint_mode)
            # Clear cache since upper lines mode affects rendering
            self.ui.renderer._clear_sprite_display_cache()
            self.ui.update_sprite_info()
    
    def handle_toggle_diamond_vertices(self):
        """Handle diamond vertices toggle"""
        if self.ui.model:
            self.ui.model.show_diamond_vertices = not self.ui.model.show_diamond_vertices
            self.ui.analysis_controls_panel.components['diamond_vertices_button'].set_text(
                f'Diamond Vertices: {"ON" if self.ui.model.show_diamond_vertices else "OFF"}'
            )
            
            # Print debug info when toggling
            print(f"\n=== DIAMOND VERTICES TOGGLE: {'ON' if self.ui.model.show_diamond_vertices else 'OFF'} ===")
            
            if self.ui.model.show_diamond_vertices:
                current_sprite = self.ui.model.get_current_sprite()
                if current_sprite and current_sprite.diamond_info:
                    diamond_info = current_sprite.diamond_info
                    print(f"Sprite {self.ui.model.current_sprite_index} Diamond Coordinates:")
                    
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
                        print(f"  effective_upper_z: {self.ui.model.get_effective_upper_z_offset(self.ui.model.current_sprite_index)}")
                else:
                    print("  No diamond analysis data available")
            
            # Clear cache since diamond vertices toggle affects rendering
            self.ui.renderer._clear_sprite_display_cache()
    
    def handle_toggle_diamond_lines(self):
        """Handle diamond lines toggle"""
        self.ui.renderer.show_diamond_lines = not self.ui.renderer.show_diamond_lines
        self.ui.analysis_controls_panel.components['diamond_lines_button'].set_text(
            f'Diamond Lines: {"ON" if self.ui.renderer.show_diamond_lines else "OFF"}'
        )
        
        print(f"Diamond Lines: {'ON' if self.ui.renderer.show_diamond_lines else 'OFF'}")
        
        # Clear cache since diamond lines toggle affects rendering
        self.ui.renderer._clear_sprite_display_cache()
    
    def handle_toggle_raycast_analysis(self):
        """Handle raycast analysis toggle"""
        self.ui.renderer.show_raycast_analysis = not self.ui.renderer.show_raycast_analysis
        self.ui.analysis_controls_panel.components['raycast_analysis_button'].set_text(
            f'Raycast Analysis: {"ON" if self.ui.renderer.show_raycast_analysis else "OFF"}'
        )
        
        print(f"Raycast Analysis: {'ON' if self.ui.renderer.show_raycast_analysis else 'OFF'}")
        
        # Clear cache since raycast analysis toggle affects rendering
        self.ui.renderer._clear_sprite_display_cache()
    
    def handle_toggle_manual_vertex_mode(self):
        """Handle manual vertex mode toggle"""
        if not self.ui.model:
            print("Please load a spritesheet first before using manual vertex mode")
            return
        
        # If sub-diamond mode is active, turn it off first
        if self.ui.renderer.sub_diamond_mode:
            self.ui.renderer.sub_diamond_mode = False
            self.ui.renderer.show_sub_diamonds = False
            self.ui.analysis_controls_panel.components['sub_diamond_mode_button'].set_text('Sub-Diamond Mode: OFF')
            print("=== SUB-DIAMOND MODE: OFF ===")
        
        self.ui.renderer.manual_vertex_mode = not self.ui.renderer.manual_vertex_mode
        self.ui.analysis_controls_panel.components['manual_vertex_button'].set_text(
            f'Manual Vertex Mode: {"ON" if self.ui.renderer.manual_vertex_mode else "OFF"}'
        )
        
        # If turning OFF manual vertex mode, also exit custom keypoints mode
        if not self.ui.renderer.manual_vertex_mode and self.ui.renderer.custom_keypoints_mode:
            self.ui.renderer.custom_keypoints_mode = False
            self.ui.analysis_controls_panel.components['delete_keypoints_button'].visible = False
            print("=== CUSTOM KEYPOINTS MODE: OFF ===")
        
        # Show/hide vertex selection info, auto-populate button, and reset vertices button
        self.ui.analysis_controls_panel.components['vertex_info_label'].visible = self.ui.renderer.manual_vertex_mode
        self.ui.analysis_controls_panel.components['auto_populate_button'].visible = self.ui.renderer.manual_vertex_mode
        self.ui.analysis_controls_panel.components['reset_vertices_button'].visible = self.ui.renderer.manual_vertex_mode
        
        if self.ui.renderer.manual_vertex_mode:
            # Auto-enable diamond vertices display when entering manual mode
            if not self.ui.model.show_diamond_vertices:
                self.ui.model.show_diamond_vertices = True
                self.ui.analysis_controls_panel.components['diamond_vertices_button'].set_text('Diamond Vertices: ON')
            
            # Update info label
            self._update_vertex_info_label()
            print(f"\n=== MANUAL VERTEX MODE: ON ===")
            print(f"Selected: {self.ui.renderer.selected_diamond.title()} {self.ui.renderer._get_vertex_name(self.ui.renderer.selected_vertex)}")
            print("Controls: 1=N, 2=S, 3=E, 4=W, F1=Lower, F2=Upper")
            print("Left-click to position, Right-click to remove")
            print("Auto-Populate: Fill missing vertices from manual ones")
        else:
            print("=== MANUAL VERTEX MODE: OFF ===")
        
        # Force complete cache clear and immediate update when entering manual mode
        self.ui.renderer._clear_sprite_display_cache()
        
        # Also update sprite info to force fresh render
        if self.ui.renderer.manual_vertex_mode:
            self.ui.update_sprite_info()
    
    def handle_toggle_sub_diamond_mode(self):
        """Handle sub-diamond mode toggle"""
        if not self.ui.model:
            print("Please load a spritesheet first before using sub-diamond mode")
            return
        
        # If manual vertex mode is active, turn it off first
        if self.ui.renderer.manual_vertex_mode:
            self.ui.renderer.manual_vertex_mode = False
            self.ui.analysis_controls_panel.components['manual_vertex_button'].set_text('Manual Vertex Mode: OFF')
            self.ui.analysis_controls_panel.components['vertex_info_label'].visible = False
            self.ui.analysis_controls_panel.components['auto_populate_button'].visible = False
            self.ui.analysis_controls_panel.components['reset_vertices_button'].visible = False
            print("=== MANUAL VERTEX MODE: OFF ===")
        
        self.ui.renderer.sub_diamond_mode = not self.ui.renderer.sub_diamond_mode
        self.ui.renderer.show_sub_diamonds = self.ui.renderer.sub_diamond_mode
        
        self.ui.analysis_controls_panel.components['sub_diamond_mode_button'].set_text(
            f'Sub-Diamond Mode: {"ON" if self.ui.renderer.sub_diamond_mode else "OFF"}'
        )
        
        if self.ui.renderer.sub_diamond_mode:
            print(f"\n=== SUB-DIAMOND MODE: ON ===")
            print(f"Layer: {self.ui.renderer.selected_sub_diamond_layer.upper()}")
            print(f"Editing: {self.ui.renderer.sub_diamond_editing_mode.upper().replace('_', ' ')}")
            print("Controls: F1/F2=Lower/Upper, F3=Cycle Layers, 1=Line of Sight, 2=Walkability")
            print("Left Click=Toggle, Right Click=None")
        else:
            print("=== SUB-DIAMOND MODE: OFF ===")
        
        # Clear cache and update display
        self.ui.renderer._clear_sprite_display_cache()
        self.ui.update_sprite_info()
    
    def _update_vertex_info_label(self):
        """Update the vertex selection info label"""
        if hasattr(self.ui.analysis_controls_panel.components, 'vertex_info_label'):
            vertex_name = self.ui.renderer._get_vertex_name(self.ui.renderer.selected_vertex)
            diamond_name = self.ui.renderer.selected_diamond.title()
            
            # Update custom diamonds list
            self._update_custom_diamonds_list()
            
            info_text = f'Selected: {diamond_name} {vertex_name} ({self.ui.renderer.selected_vertex})\n'
            info_text += 'Keys: 1234=NSEW F1/F2=Lower/Upper\n'
            info_text += 'F4=New Custom, F5/F6=Cycle Custom\n'
            
            if self.ui.renderer.custom_diamonds:
                info_text += f'Custom: {", ".join(self.ui.renderer.custom_diamonds)}\n'
            
            info_text += 'Left-click add, Right-click remove'
            self.ui.analysis_controls_panel.components['vertex_info_label'].set_text(info_text)
    
    def handle_auto_populate_vertices(self):
        """Auto-populate missing vertices for the currently selected diamond only"""
        if not self.ui.model or not self.ui.renderer.manual_vertex_mode:
            print("Auto-populate requires manual vertex mode to be enabled")
            return
        
        sprite_key = self.ui.model.current_sprite_index
        current_sprite = self.ui.model.get_current_sprite()
        if not current_sprite or not current_sprite.bbox:
            print("No sprite data available for auto-populate")
            return
        
        selected_diamond = self.ui.renderer.selected_diamond
        manual_data = self.ui.renderer.manual_vertices.get(sprite_key, {})
        diamond_data = manual_data.get(selected_diamond, {})
        
        if not diamond_data:
            print(f"No manual vertices for {selected_diamond} diamond to work with")
            return
        
        bbox = current_sprite.bbox
        # Use effective diamond width instead of bbox width for proper calculation
        effective_diamond_width = self.ui.model.get_effective_diamond_width(sprite_key)
        
        print(f"\n=== AUTO-POPULATE VERTICES FOR {selected_diamond.upper()} DIAMOND ===")
        print(f"Starting with {selected_diamond} diamond: {diamond_data}")
        print(f"Using effective diamond width: {effective_diamond_width} (bbox width: {bbox.width})")
        
        # Initialize if needed
        if sprite_key not in self.ui.renderer.manual_vertices:
            self.ui.renderer.manual_vertices[sprite_key] = {}
        if selected_diamond not in self.ui.renderer.manual_vertices[sprite_key]:
            self.ui.renderer.manual_vertices[sprite_key][selected_diamond] = {}
        
        # Complete the selected diamond using existing points
        point_count = len(diamond_data)
        if point_count >= 1:
            print(f"Completing {selected_diamond} diamond ({point_count} points)")
            completed_diamond = self._complete_diamond_from_points(diamond_data, effective_diamond_width)
            
            # Update manual vertices with completed diamond
            self.ui.renderer.manual_vertices[sprite_key][selected_diamond].update(completed_diamond)
            print(f"Completed {selected_diamond} diamond: {completed_diamond}")
            
            # Check if this creates a complete custom diamond and sync to model
            self._sync_complete_custom_diamond_to_model(sprite_key, selected_diamond)
        else:
            print(f"Need at least 1 vertex to auto-populate {selected_diamond} diamond")
        
        # Clear cache and update display
        self.ui.renderer._clear_sprite_display_cache()
        self.ui.update_sprite_info()
    
    def _complete_diamond_from_points(self, diamond_data, diamond_width):
        """Complete a diamond using improved geometric relationships and center-based calculations"""
        completed = {}
        
        # Copy existing points
        for vertex, coords in diamond_data.items():
            completed[vertex] = coords
        
        print(f"  Completing diamond with width {diamond_width} from points: {list(diamond_data.keys())}")
        
        # Method 1: Use center between North/South to derive East/West
        if 'north' in diamond_data and 'south' in diamond_data and ('east' not in completed or 'west' not in completed):
            nx, ny = diamond_data['north']
            sx, sy = diamond_data['south']
            
            # Calculate center between North and South
            center_x = (nx + sx) // 2
            center_y = (ny + sy) // 2
            
            print(f"  N/S center: ({center_x}, {center_y})")
            
            # East/West are at the center Y, offset by diamond_width/2 horizontally
            if 'east' not in completed:
                completed['east'] = (center_x + diamond_width // 2, center_y)
                print(f"  Derived East from N/S center: {completed['east']}")
                
            if 'west' not in completed:
                completed['west'] = (center_x - diamond_width // 2, center_y)
                print(f"  Derived West from N/S center: {completed['west']}")
        
        # Method 2: Use center between East/West to derive North/South
        elif 'east' in diamond_data and 'west' in diamond_data and ('north' not in completed or 'south' not in completed):
            ex, ey = diamond_data['east']
            wx, wy = diamond_data['west']
            
            # Calculate center between East and West
            center_x = (ex + wx) // 2
            center_y = (ey + wy) // 2
            
            print(f"  E/W center: ({center_x}, {center_y})")
            
            # North/South are at the center X, offset by diamond_width/4 vertically
            # (diamond height is typically width/2, so each half is width/4)
            if 'north' not in completed:
                completed['north'] = (center_x, center_y - diamond_width // 4)
                print(f"  Derived North from E/W center: {completed['north']}")
                
            if 'south' not in completed:
                completed['south'] = (center_x, center_y + diamond_width // 4)
                print(f"  Derived South from E/W center: {completed['south']}")
        
        # Method 3: Single-point completion - derive all vertices from any single point + diamond width
        elif len(diamond_data) == 1:
            vertex_name, (vx, vy) = next(iter(diamond_data.items()))
            print(f"  Single-point completion from {vertex_name}: ({vx}, {vy})")
            
            # Calculate diamond center based on which vertex we have
            if vertex_name == 'north':
                center_x, center_y = vx, vy + diamond_width // 4
            elif vertex_name == 'south':
                center_x, center_y = vx, vy - diamond_width // 4
            elif vertex_name == 'east':
                center_x, center_y = vx - diamond_width // 2, vy
            elif vertex_name == 'west':
                center_x, center_y = vx + diamond_width // 2, vy
            else:
                print(f"  Unknown vertex name: {vertex_name}")
                return completed
            
            print(f"  Calculated diamond center: ({center_x}, {center_y})")
            
            # Generate all four vertices from center
            completed['north'] = (center_x, center_y - diamond_width // 4)
            completed['south'] = (center_x, center_y + diamond_width // 4)
            completed['east'] = (center_x + diamond_width // 2, center_y)
            completed['west'] = (center_x - diamond_width // 2, center_y)
            
            print(f"  Generated complete diamond from single point:")
            for v_name, coords in completed.items():
                print(f"    {v_name}: {coords}")
        
        # Method 4: Fallback to pairwise single-point derivation
        else:
            # Apply geometric relationships to fill missing points
            # NOTE: In screen coords, Y increases downward, so "up" = smaller Y
            if 'south' in diamond_data and 'north' not in completed:
                # North is directly above South by diamond_width//2 (diamond height)
                sx, sy = diamond_data['south']
                completed['north'] = (sx, sy - diamond_width // 2)
                print(f"  Derived North from South: {completed['north']}")
                
            if 'north' in diamond_data and 'south' not in completed:
                # South is directly below North by diamond_width//2 (diamond height)
                nx, ny = diamond_data['north']
                completed['south'] = (nx, ny + diamond_width // 2)
                print(f"  Derived South from North: {completed['south']}")
                
            if 'west' in diamond_data and 'east' not in completed:
                # East is directly right of West by diamond_width
                wx, wy = diamond_data['west']
                completed['east'] = (wx + diamond_width, wy)
                print(f"  Derived East from West: {completed['east']}")
                
            if 'east' in diamond_data and 'west' not in completed:
                # West is directly left of East by diamond_width
                ex, ey = diamond_data['east']
                completed['west'] = (ex - diamond_width, ey)
                print(f"  Derived West from East: {completed['west']}")
        
        print(f"  Completed diamond: {completed}")
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
    
    def handle_toggle_custom_keypoints_mode(self):
        """Handle custom keypoints mode toggle (F3 key)"""
        if not self.ui.model:
            print("Please load a spritesheet first before using custom keypoints mode")
            return
        
        self.ui.renderer.custom_keypoints_mode = not self.ui.renderer.custom_keypoints_mode
        
        if self.ui.renderer.custom_keypoints_mode:
            print(f"\n=== CUSTOM KEYPOINTS MODE: ON ===")
            print("Left-click anywhere on the sprite to add a custom keypoint")
            print("Right-click near a keypoint to remove it")
            print("A dialog will prompt you to name new keypoints")
            print("Press F3 again to exit custom keypoints mode")
        else:
            print("=== CUSTOM KEYPOINTS MODE: OFF ===")
        
        # Show/hide delete keypoints button
        self.ui.analysis_controls_panel.components['delete_keypoints_button'].visible = self.ui.renderer.custom_keypoints_mode
        
        # Clear cache since custom keypoints mode affects rendering
        self.ui.renderer._clear_sprite_display_cache()
    
    def handle_delete_all_custom_keypoints(self):
        """Delete all custom keypoints for the current sprite"""
        if not self.ui.model:
            print("No model loaded")
            return
        
        sprite_key = self.ui.model.current_sprite_index
        
        # Remove from renderer
        if sprite_key in self.ui.renderer.custom_keypoints:
            count = len(self.ui.renderer.custom_keypoints[sprite_key])
            del self.ui.renderer.custom_keypoints[sprite_key]
            print(f"Deleted {count} custom keypoints from sprite {sprite_key}")
        else:
            print("No custom keypoints to delete for current sprite")
            return
        
        # Remove from model
        current_sprite = self.ui.model.get_current_sprite()
        if current_sprite:
            current_sprite.custom_keypoints.clear()
        
        # Clear cache and update display
        self.ui.renderer._clear_sprite_display_cache()
        self.ui.update_sprite_info()
    
    def handle_reset_manual_vertices(self):
        """Reset manual vertices to algorithmic positions for the current sprite"""
        if not self.ui.model:
            print("No model loaded")
            return
        
        sprite_key = self.ui.model.current_sprite_index
        
        # Remove from renderer
        if sprite_key in self.ui.renderer.manual_vertices:
            del self.ui.renderer.manual_vertices[sprite_key]
            print(f"Reset manual vertices to algorithmic positions for sprite {sprite_key}")
        else:
            print("No manual vertices to reset for current sprite")
            return
        
        # Clear cache and update display
        self.ui.renderer._clear_sprite_display_cache()
        self.ui.update_sprite_info()
    
    def handle_reset_view(self):
        """Handle view reset"""
        if self.ui.model:
            self.ui.model.pixeloid_multiplier = 1
            self.ui.model.pan_x = 0
            self.ui.model.pan_y = 0
            # Clear cache since pixeloid and pan affects rendering
            self.ui.renderer._clear_sprite_display_cache()
    
    def handle_center_view(self):
        """Handle view centering"""
        if self.ui.model:
            self.ui.model.pan_x = 0
            self.ui.model.pan_y = 0
            # Clear cache since pan affects rendering
            self.ui.renderer._clear_sprite_display_cache()
    
    def handle_mouse_wheel(self, event):
        """Handle mouse wheel for pixeloid adjustment with zoom-to-mouse functionality"""
        if not self.ui.model:
            return
            
        mouse_x, mouse_y = pygame.mouse.get_pos()
        drawing_area = pygame.Rect(self.LEFT_PANEL_WIDTH, 0, self.DRAWING_AREA_WIDTH, self.DRAWING_AREA_HEIGHT)
        if drawing_area.collidepoint(mouse_x, mouse_y):
            # Get current sprite to calculate coordinates
            current_sprite = self.ui.model.get_current_sprite()
            if not current_sprite:
                return
                
            # Convert mouse position to drawing area coordinates
            mouse_x_in_drawing = mouse_x - self.LEFT_PANEL_WIDTH
            mouse_y_in_drawing = mouse_y
            
            # Calculate current sprite positioning before zoom
            old_pixeloid = self.ui.model.pixeloid_multiplier
            sprite_rect = pygame.Rect(0, 0, current_sprite.original_size[0], current_sprite.original_size[1])
            
            old_display_width = sprite_rect.width * old_pixeloid
            old_display_height = sprite_rect.height * old_pixeloid
            old_base_sprite_x = (self.DRAWING_AREA_WIDTH - old_display_width) // 2
            old_base_sprite_y = (self.DRAWING_AREA_HEIGHT - old_display_height) // 2
            old_sprite_x = old_base_sprite_x + self.ui.model.pan_x
            old_sprite_y = old_base_sprite_y + self.ui.model.pan_y
            
            # Calculate which sprite pixel is under the mouse (use ACTUAL sprite position)
            sprite_pixel_x = (mouse_x_in_drawing - old_sprite_x) / old_pixeloid
            sprite_pixel_y = (mouse_y_in_drawing - old_sprite_y) / old_pixeloid
            
            print(f"DEBUG ZOOM: mouse_in_drawing=({mouse_x_in_drawing},{mouse_y_in_drawing})")
            print(f"DEBUG ZOOM: old_sprite_pos=({old_sprite_x},{old_sprite_y}) old_pixeloid={old_pixeloid}")
            print(f"DEBUG ZOOM: targeted_sprite_pixel=({sprite_pixel_x:.1f},{sprite_pixel_y:.1f})")
            
            # Apply zoom
            if event.y > 0:  # Scroll up - increase pixeloid
                new_pixeloid = min(32, self.ui.model.pixeloid_multiplier * 2)
            else:  # Scroll down - decrease pixeloid
                new_pixeloid = max(1, self.ui.model.pixeloid_multiplier // 2)
            
            print(f"DEBUG ZOOM: old_pixeloid={old_pixeloid} -> new_pixeloid={new_pixeloid}")
            
            # Only proceed if pixeloid actually changed
            if new_pixeloid != old_pixeloid:
                old_pan_x = self.ui.model.pan_x
                old_pan_y = self.ui.model.pan_y
                
                self.ui.model.pixeloid_multiplier = new_pixeloid
                
                # Calculate new sprite positioning after zoom
                new_display_width = sprite_rect.width * new_pixeloid
                new_display_height = sprite_rect.height * new_pixeloid
                new_base_sprite_x = (self.DRAWING_AREA_WIDTH - new_display_width) // 2
                new_base_sprite_y = (self.DRAWING_AREA_HEIGHT - new_display_height) // 2
                
                print(f"DEBUG ZOOM: new_base_sprite=({new_base_sprite_x},{new_base_sprite_y}) new_display_size=({new_display_width},{new_display_height})")
                
                # Calculate where the same sprite pixel would be with new zoom at center
                center_x_in_drawing = self.DRAWING_AREA_WIDTH // 2
                center_y_in_drawing = self.DRAWING_AREA_HEIGHT // 2
                
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
                self.ui.model.pan_x = int(pan_x_adjustment)
                self.ui.model.pan_y = int(pan_y_adjustment)
                
                print(f"DEBUG ZOOM: new_pan=({self.ui.model.pan_x},{self.ui.model.pan_y})")
                
                # Calculate final sprite position
                final_sprite_x = new_base_sprite_x + self.ui.model.pan_x
                final_sprite_y = new_base_sprite_y + self.ui.model.pan_y
                
                # Calculate where targeted pixel actually ends up
                final_target_x = final_sprite_x + sprite_pixel_x * new_pixeloid
                final_target_y = final_sprite_y + sprite_pixel_y * new_pixeloid
                
                print(f"DEBUG ZOOM: final_sprite_pos=({final_sprite_x},{final_sprite_y})")
                print(f"DEBUG ZOOM: final_target_pos=({final_target_x:.1f},{final_target_y:.1f})")
                print(f"DEBUG ZOOM: center_error=({final_target_x - center_x_in_drawing:.1f},{final_target_y - center_y_in_drawing:.1f})")
                
                # Note: Skip pan constraints during zoom-to-center operations
                # to allow the image to move freely to center the targeted pixel
                
                # Update UI and clear cache
                self.ui.renderer._clear_sprite_display_cache()
    
    def handle_mouse_motion(self, event):
        """Handle mouse motion to track pixeloid position"""
        self.ui.mouse_x = event.pos[0]
        self.ui.mouse_y = event.pos[1]
        
        # Check if mouse is in drawing area
        drawing_area = pygame.Rect(self.LEFT_PANEL_WIDTH, 0, self.DRAWING_AREA_WIDTH, self.DRAWING_AREA_HEIGHT)
        self.ui.mouse_in_drawing_area = drawing_area.collidepoint(self.ui.mouse_x, self.ui.mouse_y)
        
        if self.ui.mouse_in_drawing_area and self.ui.model:
            current_sprite = self.ui.model.get_current_sprite()
            if current_sprite:
                # Convert mouse position to drawing area coordinates
                mouse_x_in_drawing = self.ui.mouse_x - self.LEFT_PANEL_WIDTH
                mouse_y_in_drawing = self.ui.mouse_y
                
                # Calculate expanded bounds if diamond extends beyond bbox
                expanded_bounds = self.ui.renderer._calculate_expanded_bounds(current_sprite, self.ui.model)
                
                sprite_rect = pygame.Rect(0, 0, current_sprite.original_size[0], current_sprite.original_size[1])
                
                if expanded_bounds and expanded_bounds['diamond_extends']:
                    # Use expanded bounds for positioning calculations
                    expanded_display_width = expanded_bounds['width'] * self.ui.model.pixeloid_multiplier
                    expanded_display_height = expanded_bounds['height'] * self.ui.model.pixeloid_multiplier
                    
                    # Center the expanded area
                    base_expanded_x = (self.DRAWING_AREA_WIDTH - expanded_display_width) // 2
                    base_expanded_y = (self.DRAWING_AREA_HEIGHT - expanded_display_height) // 2
                    
                    # Calculate sprite offset within expanded area
                    bbox_offset_x = (expanded_bounds['original_bbox'].x - expanded_bounds['x']) * self.ui.model.pixeloid_multiplier
                    bbox_offset_y = (expanded_bounds['original_bbox'].y - expanded_bounds['y']) * self.ui.model.pixeloid_multiplier
                    
                    sprite_x = base_expanded_x + bbox_offset_x + self.ui.model.pan_x
                    sprite_y = base_expanded_y + bbox_offset_y + self.ui.model.pan_y
                else:
                    # Use original positioning logic
                    display_width = sprite_rect.width * self.ui.model.pixeloid_multiplier
                    display_height = sprite_rect.height * self.ui.model.pixeloid_multiplier
                    base_sprite_x = (self.DRAWING_AREA_WIDTH - display_width) // 2
                    base_sprite_y = (self.DRAWING_AREA_HEIGHT - display_height) // 2
                    sprite_x = base_sprite_x + self.ui.model.pan_x
                    sprite_y = base_sprite_y + self.ui.model.pan_y
                
                # Calculate which sprite pixel is under the mouse
                self.ui.sprite_pixel_x = (mouse_x_in_drawing - sprite_x) / self.ui.model.pixeloid_multiplier
                self.ui.sprite_pixel_y = (mouse_y_in_drawing - sprite_y) / self.ui.model.pixeloid_multiplier
                
                # Clamp to sprite bounds
                self.ui.sprite_pixel_x = max(0, min(current_sprite.original_size[0] - 1, self.ui.sprite_pixel_x))
                self.ui.sprite_pixel_y = max(0, min(current_sprite.original_size[1] - 1, self.ui.sprite_pixel_y))
    
    def handle_left_click(self, event):
        """Handle left-click for adding manual vertices, custom keypoints, or sub-diamond editing"""
        if not self.ui.model:
            return
        
        # Check sub-diamond mode first
        if self.ui.renderer.sub_diamond_mode and self.handle_sub_diamond_click(event):
            return
        
        # Check if we're in any supported mode
        if not (self.ui.renderer.manual_vertex_mode or self.ui.renderer.custom_keypoints_mode):
            return
        
        mouse_x, mouse_y = event.pos
        drawing_area = pygame.Rect(self.LEFT_PANEL_WIDTH, 0, self.DRAWING_AREA_WIDTH, self.DRAWING_AREA_HEIGHT)
        
        if not drawing_area.collidepoint(mouse_x, mouse_y):
            return  # Click outside drawing area
        
        current_sprite = self.ui.model.get_current_sprite()
        if not current_sprite:
            return
        
        # Convert mouse position to sprite pixel coordinates (shared logic)
        original_x, original_y = self._convert_mouse_to_sprite_coords(event.pos, current_sprite)
        
        if self.ui.renderer.custom_keypoints_mode:
            self._handle_custom_keypoint_add(original_x, original_y)
        elif self.ui.renderer.manual_vertex_mode:
            self._handle_manual_vertex_add(original_x, original_y, event.pos)
    
    def handle_right_click(self, event):
        """Handle right-click for removing manual vertices, custom keypoints, or sub-diamond editing"""
        if not self.ui.model:
            return
        
        # Check sub-diamond mode first
        if self.ui.renderer.sub_diamond_mode and self.handle_sub_diamond_click(event):
            return
        
        # Check if we're in any supported mode
        if not (self.ui.renderer.manual_vertex_mode or self.ui.renderer.custom_keypoints_mode):
            return
        
        mouse_x, mouse_y = event.pos
        drawing_area = pygame.Rect(self.LEFT_PANEL_WIDTH, 0, self.DRAWING_AREA_WIDTH, self.DRAWING_AREA_HEIGHT)
        
        if not drawing_area.collidepoint(mouse_x, mouse_y):
            return  # Click outside drawing area
        
        current_sprite = self.ui.model.get_current_sprite()
        if not current_sprite:
            return
        
        # Convert mouse position to sprite pixel coordinates
        original_x, original_y = self._convert_mouse_to_sprite_coords(event.pos, current_sprite)
        
        if self.ui.renderer.custom_keypoints_mode:
            self._handle_custom_keypoint_remove(original_x, original_y)
        elif self.ui.renderer.manual_vertex_mode:
            self._handle_manual_vertex_remove(original_x, original_y)
    
    def _convert_mouse_to_sprite_coords(self, mouse_pos, current_sprite):
        """Convert mouse position to sprite pixel coordinates, accounting for expanded bounds"""
        mouse_x, mouse_y = mouse_pos
        mouse_x_in_drawing = mouse_x - self.LEFT_PANEL_WIDTH
        mouse_y_in_drawing = mouse_y
        
        # Calculate expanded bounds if diamond extends beyond bbox
        expanded_bounds = self.ui.renderer._calculate_expanded_bounds(current_sprite, self.ui.model)
        
        sprite_rect = pygame.Rect(0, 0, current_sprite.original_size[0], current_sprite.original_size[1])
        
        if expanded_bounds and expanded_bounds['diamond_extends']:
            # Use expanded bounds for positioning calculations
            expanded_display_width = expanded_bounds['width'] * self.ui.model.pixeloid_multiplier
            expanded_display_height = expanded_bounds['height'] * self.ui.model.pixeloid_multiplier
            
            # Center the expanded area
            base_expanded_x = (self.DRAWING_AREA_WIDTH - expanded_display_width) // 2
            base_expanded_y = (self.DRAWING_AREA_HEIGHT - expanded_display_height) // 2
            
            # Calculate sprite offset within expanded area
            bbox_offset_x = (expanded_bounds['original_bbox'].x - expanded_bounds['x']) * self.ui.model.pixeloid_multiplier
            bbox_offset_y = (expanded_bounds['original_bbox'].y - expanded_bounds['y']) * self.ui.model.pixeloid_multiplier
            
            sprite_x = base_expanded_x + bbox_offset_x + self.ui.model.pan_x
            sprite_y = base_expanded_y + bbox_offset_y + self.ui.model.pan_y
        else:
            # Use original positioning logic
            display_width = sprite_rect.width * self.ui.model.pixeloid_multiplier
            display_height = sprite_rect.height * self.ui.model.pixeloid_multiplier
            base_sprite_x = (self.DRAWING_AREA_WIDTH - display_width) // 2
            base_sprite_y = (self.DRAWING_AREA_HEIGHT - display_height) // 2
            sprite_x = base_sprite_x + self.ui.model.pan_x
            sprite_y = base_sprite_y + self.ui.model.pan_y
        
        # Calculate which sprite pixel was clicked
        sprite_pixel_x = (mouse_x_in_drawing - sprite_x) / self.ui.model.pixeloid_multiplier
        sprite_pixel_y = (mouse_y_in_drawing - sprite_y) / self.ui.model.pixeloid_multiplier
        
        # Clamp to sprite bounds
        sprite_pixel_x = max(0, min(current_sprite.original_size[0] - 1, sprite_pixel_x))
        sprite_pixel_y = max(0, min(current_sprite.original_size[1] - 1, sprite_pixel_y))
        
        return int(sprite_pixel_x), int(sprite_pixel_y)
    
    def _handle_custom_keypoint_add(self, original_x, original_y):
        """Handle left-click in custom keypoints mode to add keypoint"""
        sprite_key = self.ui.model.current_sprite_index
        
        # Show text input dialog for keypoint name
        keypoint_name = self._show_keypoint_name_dialog(original_x, original_y)
        
        if keypoint_name and keypoint_name.strip():
            # Store the custom keypoint
            if sprite_key not in self.ui.renderer.custom_keypoints:
                self.ui.renderer.custom_keypoints[sprite_key] = {}
            
            # Store keypoint with cleaned name
            clean_name = keypoint_name.strip()
            self.ui.renderer.custom_keypoints[sprite_key][clean_name] = (original_x, original_y)
            
            # Also store in the model for JSON persistence
            current_sprite = self.ui.model.get_current_sprite()
            if current_sprite:
                from spritesheet_model import Point
                current_sprite.custom_keypoints[clean_name] = Point(x=original_x, y=original_y)
            
            print(f"Added custom keypoint '{clean_name}' at ({original_x}, {original_y})")
            
            # Clear cache and update display
            self.ui.renderer._clear_sprite_display_cache()
            self.ui.update_sprite_info()
        else:
            print("Keypoint creation cancelled or invalid name provided")
    
    def _show_keypoint_name_dialog(self, x, y):
        """Show a simple text input dialog for keypoint naming"""
        try:
            import tkinter as tk
            from tkinter import simpledialog
            
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            # Show input dialog
            keypoint_name = simpledialog.askstring(
                "Custom Keypoint",
                f"Enter name for keypoint at ({x}, {y}):",
                initialvalue=""
            )
            
            root.destroy()
            return keypoint_name
            
        except Exception as e:
            print(f"Error showing keypoint name dialog: {e}")
            return None
    
    def _handle_manual_vertex_add(self, original_x, original_y, mouse_pos):
        """Handle left-click in manual vertex mode to add vertex"""
        mouse_x, mouse_y = mouse_pos
        mouse_x_in_drawing = mouse_x - self.LEFT_PANEL_WIDTH
        mouse_y_in_drawing = mouse_y
        
        current_sprite = self.ui.model.get_current_sprite()
        
        # Calculate expanded bounds if diamond extends beyond bbox
        expanded_bounds = self.ui.renderer._calculate_expanded_bounds(current_sprite, self.ui.model)
        
        sprite_rect = pygame.Rect(0, 0, current_sprite.original_size[0], current_sprite.original_size[1])
        
        if expanded_bounds and expanded_bounds['diamond_extends']:
            # Use expanded bounds for positioning calculations
            expanded_display_width = expanded_bounds['width'] * self.ui.model.pixeloid_multiplier
            expanded_display_height = expanded_bounds['height'] * self.ui.model.pixeloid_multiplier
            
            # Center the expanded area
            base_expanded_x = (self.DRAWING_AREA_WIDTH - expanded_display_width) // 2
            base_expanded_y = (self.DRAWING_AREA_HEIGHT - expanded_display_height) // 2
            
            # Calculate sprite offset within expanded area
            bbox_offset_x = (expanded_bounds['original_bbox'].x - expanded_bounds['x']) * self.ui.model.pixeloid_multiplier
            bbox_offset_y = (expanded_bounds['original_bbox'].y - expanded_bounds['y']) * self.ui.model.pixeloid_multiplier
            
            sprite_x = base_expanded_x + bbox_offset_x + self.ui.model.pan_x
            sprite_y = base_expanded_y + bbox_offset_y + self.ui.model.pan_y
        else:
            # Use original positioning logic
            display_width = sprite_rect.width * self.ui.model.pixeloid_multiplier
            display_height = sprite_rect.height * self.ui.model.pixeloid_multiplier
            base_sprite_x = (self.DRAWING_AREA_WIDTH - display_width) // 2
            base_sprite_y = (self.DRAWING_AREA_HEIGHT - display_height) // 2
            sprite_x = base_sprite_x + self.ui.model.pan_x
            sprite_y = base_sprite_y + self.ui.model.pan_y
        
        sprite_pixel_x = (mouse_x_in_drawing - sprite_x) / self.ui.model.pixeloid_multiplier
        sprite_pixel_y = (mouse_y_in_drawing - sprite_y) / self.ui.model.pixeloid_multiplier
        
        print(f"DEBUG CLICK: mouse_in_drawing=({mouse_x_in_drawing},{mouse_y_in_drawing})")
        print(f"DEBUG CLICK: sprite_pos=({sprite_x},{sprite_y}) pixeloid={self.ui.model.pixeloid_multiplier}")
        print(f"DEBUG CLICK: raw_sprite_pixel=({sprite_pixel_x:.1f},{sprite_pixel_y:.1f})")
        print(f"DEBUG CLICK: clamped_sprite_pixel=({sprite_pixel_x:.1f},{sprite_pixel_y:.1f})")
        print(f"DEBUG CLICK: sprite_pixel=({sprite_pixel_x:.1f},{sprite_pixel_y:.1f}) -> absolute=({original_x},{original_y})")
        if expanded_bounds and expanded_bounds['diamond_extends']:
            print(f"DEBUG CLICK: Using expanded bounds - diamond extends beyond bbox")
        
        # Store the manual vertex position
        sprite_key = self.ui.model.current_sprite_index
        if sprite_key not in self.ui.renderer.manual_vertices:
            self.ui.renderer.manual_vertices[sprite_key] = {}
        
        if self.ui.renderer.selected_diamond not in self.ui.renderer.manual_vertices[sprite_key]:
            self.ui.renderer.manual_vertices[sprite_key][self.ui.renderer.selected_diamond] = {}
        
        vertex_name = self.ui.renderer._get_vertex_name(self.ui.renderer.selected_vertex).lower()
        self.ui.renderer.manual_vertices[sprite_key][self.ui.renderer.selected_diamond][vertex_name] = (original_x, original_y)
        
        # Log the positioning
        print(f"Positioned {self.ui.renderer.selected_diamond} {vertex_name} at ({original_x}, {original_y}) "
              f"[sprite pixel: ({sprite_pixel_x:.1f}, {sprite_pixel_y:.1f})]")
        print(f"DEBUG STORAGE: manual_vertices after positioning = {self.ui.renderer.manual_vertices}")
        
        # Check if this completes a custom diamond and sync to model
        self._sync_complete_custom_diamond_to_model(sprite_key, self.ui.renderer.selected_diamond)
        
        # Clear cache to trigger re-render with new vertex position
        self.ui.renderer._clear_sprite_display_cache()
        
        # Update measurements display to show new manual coordinates
        self.ui.update_sprite_info()
    
    def _handle_custom_keypoint_remove(self, original_x, original_y):
        """Handle right-click in custom keypoints mode to remove nearest keypoint"""
        sprite_key = self.ui.model.current_sprite_index
        
        if sprite_key not in self.ui.renderer.custom_keypoints:
            print("No custom keypoints to remove for this sprite")
            return
        
        keypoints = self.ui.renderer.custom_keypoints[sprite_key]
        if not keypoints:
            print("No custom keypoints to remove for this sprite")
            return
        
        # Find the closest keypoint within a reasonable distance (10 pixels)
        closest_keypoint = None
        closest_distance = float('inf')
        removal_threshold = 10  # pixels
        
        for keypoint_name, (kp_x, kp_y) in keypoints.items():
            distance = ((original_x - kp_x) ** 2 + (original_y - kp_y) ** 2) ** 0.5
            if distance < removal_threshold and distance < closest_distance:
                closest_distance = distance
                closest_keypoint = keypoint_name
        
        if closest_keypoint:
            # Remove from renderer
            del self.ui.renderer.custom_keypoints[sprite_key][closest_keypoint]
            if not self.ui.renderer.custom_keypoints[sprite_key]:
                del self.ui.renderer.custom_keypoints[sprite_key]
            
            # Remove from model
            current_sprite = self.ui.model.get_current_sprite()
            if current_sprite and closest_keypoint in current_sprite.custom_keypoints:
                del current_sprite.custom_keypoints[closest_keypoint]
            
            print(f"Removed custom keypoint '{closest_keypoint}'")
            
            # Clear cache and update display
            self.ui.renderer._clear_sprite_display_cache()
            self.ui.update_sprite_info()
        else:
            print(f"No custom keypoint found near ({original_x}, {original_y})")
    
    def _handle_manual_vertex_remove(self, original_x, original_y):
        """Handle right-click in manual vertex mode to remove nearest manual vertex"""
        sprite_key = self.ui.model.current_sprite_index
        
        if sprite_key not in self.ui.renderer.manual_vertices:
            print("No manual vertices to remove for this sprite")
            return
        
        # Find the closest manual vertex within a reasonable distance (10 pixels)
        closest_vertex = None
        closest_diamond = None
        closest_distance = float('inf')
        removal_threshold = 10  # pixels
        
        # Check all diamond levels including custom diamonds
        all_diamond_levels = ['lower', 'upper']
        current_sprite = self.ui.model.get_current_sprite()
        if current_sprite and current_sprite.diamond_info and current_sprite.diamond_info.extra_diamonds:
            all_diamond_levels.extend(current_sprite.diamond_info.extra_diamonds.keys())
        
        for diamond_level in all_diamond_levels:
            if diamond_level in self.ui.renderer.manual_vertices[sprite_key]:
                vertices = self.ui.renderer.manual_vertices[sprite_key][diamond_level]
                for vertex_name, (v_x, v_y) in vertices.items():
                    distance = ((original_x - v_x) ** 2 + (original_y - v_y) ** 2) ** 0.5
                    if distance < removal_threshold and distance < closest_distance:
                        closest_distance = distance
                        closest_vertex = vertex_name
                        closest_diamond = diamond_level
        
        if closest_vertex and closest_diamond:
            # Remove the manual vertex
            del self.ui.renderer.manual_vertices[sprite_key][closest_diamond][closest_vertex]
            
            # Clean up empty dictionaries
            if not self.ui.renderer.manual_vertices[sprite_key][closest_diamond]:
                del self.ui.renderer.manual_vertices[sprite_key][closest_diamond]
            if not self.ui.renderer.manual_vertices[sprite_key]:
                del self.ui.renderer.manual_vertices[sprite_key]
            
            print(f"Removed manual vertex: {closest_diamond} {closest_vertex}")
            
            # Clear cache and update display
            self.ui.renderer._clear_sprite_display_cache()
            self.ui.update_sprite_info()
        else:
            print(f"No manual vertex found near ({original_x}, {original_y})")
    
    def handle_manual_vertex_keys(self, key):
        """Handle keyboard input for manual vertex mode and custom keypoints mode"""
        # Handle sub-diamond mode keys first
        if self.handle_sub_diamond_keys(key):
            return
        
        # F3 key toggles custom keypoints mode (works regardless of other modes)
        if key == pygame.K_F3:
            self.handle_toggle_custom_keypoints_mode()
            return
        
        # F4 key creates new custom diamond
        if key == pygame.K_F4:
            self.handle_create_custom_diamond()
            return
        
        # F1/F2 keys should exit custom keypoints mode and enter manual vertex mode
        if key in [pygame.K_F1, pygame.K_F2]:
            if self.ui.renderer.custom_keypoints_mode:
                # Exit custom keypoints mode
                self.ui.renderer.custom_keypoints_mode = False
                self.ui.analysis_controls_panel.components['delete_keypoints_button'].visible = False
                print("=== CUSTOM KEYPOINTS MODE: OFF ===")
                
                # Enter manual vertex mode if not already active
                if not self.ui.renderer.manual_vertex_mode:
                    self.ui.renderer.manual_vertex_mode = True
                    self.ui.analysis_controls_panel.components['manual_vertex_button'].set_text('Manual Vertex Mode: ON')
                    self.ui.analysis_controls_panel.components['vertex_info_label'].visible = True
                    self.ui.analysis_controls_panel.components['auto_populate_button'].visible = True
                    self.ui.analysis_controls_panel.components['reset_vertices_button'].visible = True
                    
                    # Auto-enable diamond vertices display when entering manual mode
                    if not self.ui.model.show_diamond_vertices:
                        self.ui.model.show_diamond_vertices = True
                        self.ui.analysis_controls_panel.components['diamond_vertices_button'].set_text('Diamond Vertices: ON')
                    
                    print(f"\n=== MANUAL VERTEX MODE: ON ===")
        
        if not self.ui.renderer.manual_vertex_mode:
            return
        
        # Number keys 1-4 for vertex selection (N, S, E, W)
        if key == pygame.K_1:
            self.ui.renderer.selected_vertex = 1  # North
        elif key == pygame.K_2:
            self.ui.renderer.selected_vertex = 2  # South
        elif key == pygame.K_3:
            self.ui.renderer.selected_vertex = 3  # East
        elif key == pygame.K_4:
            self.ui.renderer.selected_vertex = 4  # West
        # F1/F2 for diamond selection
        elif key == pygame.K_F1:
            self.ui.renderer.selected_diamond = 'lower'
            self.ui.renderer.selected_custom_diamond_index = -1
        elif key == pygame.K_F2:
            self.ui.renderer.selected_diamond = 'upper'
            self.ui.renderer.selected_custom_diamond_index = -1
        # F5/F6 for cycling through custom diamonds
        elif key == pygame.K_F5:
            self.handle_cycle_custom_diamond(-1)  # Previous
        elif key == pygame.K_F6:
            self.handle_cycle_custom_diamond(1)   # Next
        else:
            return  # Key not handled
        
        # Update UI and clear cache
        self._update_vertex_info_label()
        vertex_name = self.ui.renderer._get_vertex_name(self.ui.renderer.selected_vertex)
        print(f"Selected: {self.ui.renderer.selected_diamond.title()} {vertex_name} ({self.ui.renderer.selected_vertex})")
        self.ui.renderer._clear_sprite_display_cache()
    
    def update_panning(self, keys_pressed):
        """Update panning based on currently pressed keys"""
        if not self.ui.model or not self.ui.analyzer:
            return
            
        # Pan speed - scale with pixeloid multiplier for responsive movement
        base_pan_speed = 5
        pan_speed = base_pan_speed * self.ui.model.pixeloid_multiplier
        
        # WASD movement
        if pygame.K_w in keys_pressed:
            self.ui.model.pan_y += pan_speed
        if pygame.K_s in keys_pressed:
            self.ui.model.pan_y -= pan_speed
        if pygame.K_a in keys_pressed:
            self.ui.model.pan_x += pan_speed
        if pygame.K_d in keys_pressed:
            self.ui.model.pan_x -= pan_speed
        
        # Constrain panning to reasonable bounds
        current_sprite = self.ui.model.get_current_sprite()
        if current_sprite:
            display_width = current_sprite.original_size[0] * self.ui.model.pixeloid_multiplier
            display_height = current_sprite.original_size[1] * self.ui.model.pixeloid_multiplier
            
            max_pan_x = max(0, (display_width - self.DRAWING_AREA_WIDTH) // 2 + 200)
            max_pan_y = max(0, (display_height - self.DRAWING_AREA_HEIGHT) // 2 + 200)
            
            self.ui.model.pan_x = max(-max_pan_x, min(max_pan_x, self.ui.model.pan_x))
            self.ui.model.pan_y = max(-max_pan_y, min(max_pan_y, self.ui.model.pan_y))
    
    def save_analysis_data(self):
        """Save the current analysis data to JSON with manual vertices replacing algorithmic ones"""
        if not self.ui.model:
            print("No model to save")
            return
        
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            
            # Create default filename
            sprite_name = Path(self.ui.model.image_path).stem
            default_name = f"{sprite_name}_analysis.json"
            
            file_path = filedialog.asksaveasfilename(
                initialdir=self.DEFAULT_SAVE_DIR,
                initialfile=default_name,
                title="Save Analysis Data",
                filetypes=[("JSON files", "*.json")]
            )
            root.destroy()
            
            if file_path:
                # Pass manual vertices to model for correct midpoint calculation
                self.ui.model.set_manual_vertices_for_export(self.ui.renderer.manual_vertices)
                
                # Sync custom keypoints from renderer to model
                self._sync_custom_keypoints_to_model()
                
                try:
                    # Save with manual vertices and custom keypoints as the primary data
                    self.ui.model.save_to_json(file_path)
                    manual_count = len([s for s in self.ui.model.sprites if s.diamond_info and self._has_manual_vertices_for_sprite(s.sprite_index)])
                    keypoints_count = len([s for s in self.ui.model.sprites if s.custom_keypoints])
                    total_count = len([s for s in self.ui.model.sprites if s.diamond_info])
                    print(f"Analysis data saved to: {file_path}")
                    print(f"Manual vertices applied to {manual_count}/{total_count} sprites with diamond data")
                    print(f"Custom keypoints saved for {keypoints_count} sprites")
                    
                finally:
                    # Clear manual vertices from model (so runtime behavior unchanged)
                    self.ui.model._renderer_manual_vertices = {}
                
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
                initialdir=self.DEFAULT_SAVE_DIR,
                title="Load Analysis Data",
                filetypes=[("JSON files", "*.json")]
            )
            root.destroy()
            
            if file_path:
                # Load the model
                self.ui.model = SpritesheetModel.load_from_json(file_path)
                
                # Try to load the original image
                if os.path.exists(self.ui.model.image_path):
                    self.ui.load_spritesheet(self.ui.model.image_path)
                    self.ui.analyzer = SpriteAnalyzer(self.ui.model)
                    if self.ui.spritesheet_surface:  # Fix Pylance warning
                        self.ui.analyzer.load_spritesheet_surface(self.ui.spritesheet_surface)
                else:
                    print(f"Warning: Original image not found at {self.ui.model.image_path}")
                    print("Please load the spritesheet manually")
                
                # Update UI controls
                self.ui.file_ops_panel.components['rows_input'].set_text(str(self.ui.model.rows))
                self.ui.file_ops_panel.components['cols_input'].set_text(str(self.ui.model.cols))
                self.ui.analysis_controls_panel.components['threshold_slider'].set_current_value(self.ui.model.alpha_threshold)
                self.ui.analysis_controls_panel.components['global_z_input'].set_text(str(self.ui.model.upper_z_offset))
                
                # Sync custom keypoints from model to renderer
                self._sync_custom_keypoints_from_model()
                
                # Transfer diamond vertices from model to renderer as manual vertices
                self.ui.model.transfer_vertices_to_manual(self.ui.renderer)
                
                self.ui.update_sprite_info()
                print(f"Analysis data loaded from: {file_path}")
                
        except Exception as e:
            print(f"Error loading analysis data: {e}")
    
    def _apply_manual_vertices_to_model(self):
        """Temporarily replace algorithmic diamond vertices with manual ones for saving"""
        if not hasattr(self.ui.renderer, 'manual_vertices') or not self.ui.renderer.manual_vertices:
            return {}  # No manual vertices to apply
        
        original_data = {}
        
        for sprite_index, manual_sprite_data in self.ui.renderer.manual_vertices.items():
            if sprite_index >= len(self.ui.model.sprites):
                continue
                
            sprite = self.ui.model.sprites[sprite_index]
            if not sprite.diamond_info:
                continue  # No diamond data to replace
            
            # Store original diamond data
            original_data[sprite_index] = {
                'lower_diamond': sprite.diamond_info.lower_diamond.model_copy() if sprite.diamond_info.lower_diamond else None,
                'upper_diamond': sprite.diamond_info.upper_diamond.model_copy() if sprite.diamond_info.upper_diamond else None
            }
            
            # Replace lower diamond vertices with manual ones
            if 'lower' in manual_sprite_data and sprite.diamond_info.lower_diamond:
                self._apply_manual_vertices_to_diamond(sprite.diamond_info.lower_diamond, manual_sprite_data['lower'])
            
            # Replace upper diamond vertices with manual ones
            if 'upper' in manual_sprite_data and sprite.diamond_info.upper_diamond:
                self._apply_manual_vertices_to_diamond(sprite.diamond_info.upper_diamond, manual_sprite_data['upper'])
            
            # Replace custom diamond vertices with manual ones
            for diamond_name, custom_diamond in sprite.diamond_info.extra_diamonds.items():
                if diamond_name in manual_sprite_data:
                    self._apply_manual_vertices_to_diamond(custom_diamond, manual_sprite_data[diamond_name])
            
            # Recalculate diamonds_z_offset based on actual manual vertex positions
            if sprite.diamond_info.lower_diamond and sprite.diamond_info.upper_diamond:
                lower_north_y = sprite.diamond_info.lower_diamond.north_vertex.y
                upper_north_y = sprite.diamond_info.upper_diamond.north_vertex.y
                sprite.diamond_info.diamonds_z_offset = lower_north_y - upper_north_y
                print(f"Recalculated diamonds_z_offset for sprite {sprite_index}: {sprite.diamond_info.diamonds_z_offset} (lower: {lower_north_y}, upper: {upper_north_y})")
            else:
                sprite.diamond_info.diamonds_z_offset = None
        
        return original_data
    
    def _apply_manual_vertices_to_diamond(self, diamond_data, manual_vertices):
        """Apply manual vertex coordinates to a diamond data object"""
        from spritesheet_model import Point
        
        if 'north' in manual_vertices:
            x, y = manual_vertices['north']
            diamond_data.north_vertex = Point(x=x, y=y)
        
        if 'south' in manual_vertices:
            x, y = manual_vertices['south']
            diamond_data.south_vertex = Point(x=x, y=y)
        
        if 'east' in manual_vertices:
            x, y = manual_vertices['east']
            diamond_data.east_vertex = Point(x=x, y=y)
        
        if 'west' in manual_vertices:
            x, y = manual_vertices['west']
            diamond_data.west_vertex = Point(x=x, y=y)
    
    def _restore_original_diamond_data(self, original_data):
        """Restore original algorithmic diamond data after saving"""
        for sprite_index, diamond_backup in original_data.items():
            if sprite_index >= len(self.ui.model.sprites):
                continue
                
            sprite = self.ui.model.sprites[sprite_index]
            if not sprite.diamond_info:
                continue
            
            # Restore original diamond data
            if diamond_backup['lower_diamond']:
                sprite.diamond_info.lower_diamond = diamond_backup['lower_diamond']
            
            if diamond_backup['upper_diamond']:
                sprite.diamond_info.upper_diamond = diamond_backup['upper_diamond']
    
    def _sync_custom_keypoints_to_model(self):
        """Sync custom keypoints from renderer to model for JSON persistence"""
        if not hasattr(self.ui.renderer, 'custom_keypoints') or not self.ui.renderer.custom_keypoints:
            return
        
        from spritesheet_model import Point
        
        for sprite_index, keypoints in self.ui.renderer.custom_keypoints.items():
            if sprite_index >= len(self.ui.model.sprites):
                continue
                
            sprite = self.ui.model.sprites[sprite_index]
            
            # Clear existing custom keypoints in model
            sprite.custom_keypoints.clear()
            
            # Add all keypoints from renderer to model
            for keypoint_name, (x, y) in keypoints.items():
                sprite.custom_keypoints[keypoint_name] = Point(x=x, y=y)
    
    def _sync_custom_keypoints_from_model(self):
        """Sync custom keypoints from model to renderer after loading"""
        if not hasattr(self.ui.renderer, 'custom_keypoints'):
            self.ui.renderer.custom_keypoints = {}
        
        # Clear existing custom keypoints in renderer
        self.ui.renderer.custom_keypoints.clear()
        
        for sprite_index, sprite in enumerate(self.ui.model.sprites):
            if sprite.custom_keypoints:
                self.ui.renderer.custom_keypoints[sprite_index] = {}
                for keypoint_name, point in sprite.custom_keypoints.items():
                    self.ui.renderer.custom_keypoints[sprite_index][keypoint_name] = (point.x, point.y)
    
    def _has_manual_vertices_for_sprite(self, sprite_index):
        """Check if a sprite has any manual vertices defined"""
        if not hasattr(self.ui.renderer, 'manual_vertices') or not self.ui.renderer.manual_vertices:
            return False
        
        return sprite_index in self.ui.renderer.manual_vertices and len(self.ui.renderer.manual_vertices[sprite_index]) > 0
    
    def handle_create_custom_diamond(self):
        """Handle F4 key to create a new custom diamond"""
        if not self.ui.model:
            print("Please load a spritesheet first before creating custom diamonds")
            return
        
        current_sprite = self.ui.model.get_current_sprite()
        if not current_sprite or not current_sprite.diamond_info:
            print("No diamond analysis data available for creating custom diamonds")
            return
        
        # Show dialog to get diamond name
        diamond_name = self._show_diamond_name_dialog()
        if not diamond_name or not diamond_name.strip():
            print("Custom diamond creation cancelled")
            return
        
        clean_name = diamond_name.strip()
        
        # Check if name already exists
        if clean_name in current_sprite.diamond_info.extra_diamonds:
            print(f"Custom diamond '{clean_name}' already exists")
            return
        
        # Create a new empty diamond with default z_offset
        from spritesheet_model import GameplayDiamondData, Point
        
        # Start with a template based on lower diamond but with custom z_offset
        template = current_sprite.diamond_info.lower_diamond
        custom_z_offset = 50.0  # Default offset
        
        # Create a temporary SingleDiamondData for conversion
        from spritesheet_model import SingleDiamondData
        temp_diamond = SingleDiamondData(
            north_vertex=Point(x=template.north_vertex.x, y=template.north_vertex.y - int(custom_z_offset)),
            south_vertex=Point(x=template.south_vertex.x, y=template.south_vertex.y - int(custom_z_offset)),
            east_vertex=Point(x=template.east_vertex.x, y=template.east_vertex.y - int(custom_z_offset)),
            west_vertex=Point(x=template.west_vertex.x, y=template.west_vertex.y - int(custom_z_offset)),
            center=Point(x=template.center.x, y=template.center.y - int(custom_z_offset)),
            z_offset=custom_z_offset
        )
        
        # Convert to GameplayDiamondData to include sub_diamonds and edge properties
        new_diamond = GameplayDiamondData.from_single_diamond(temp_diamond)
        
        # Add to model
        current_sprite.diamond_info.extra_diamonds[clean_name] = new_diamond
        
        # Update renderer's custom diamonds list
        self._update_custom_diamonds_list()
        
        # Select the new custom diamond
        self.ui.renderer.selected_diamond = clean_name
        self.ui.renderer.selected_custom_diamond_index = len(self.ui.renderer.custom_diamonds) - 1
        
        print(f"Created custom diamond '{clean_name}' with z_offset {custom_z_offset}")
        print(f"Selected custom diamond: {clean_name}")
        
        # Clear cache and update display
        self.ui.renderer._clear_sprite_display_cache()
        self._update_vertex_info_label()
    
    def handle_cycle_custom_diamond(self, direction):
        """Handle F5/F6 keys to cycle through custom diamonds"""
        if not self.ui.model:
            return
        
        # Update custom diamonds list
        self._update_custom_diamonds_list()
        
        if not self.ui.renderer.custom_diamonds:
            print("No custom diamonds available")
            return
        
        # Cycle through custom diamonds
        if self.ui.renderer.selected_custom_diamond_index == -1:
            # Not currently on a custom diamond, select first
            self.ui.renderer.selected_custom_diamond_index = 0 if direction > 0 else len(self.ui.renderer.custom_diamonds) - 1
        else:
            # Cycle to next/previous
            self.ui.renderer.selected_custom_diamond_index += direction
            
            # Wrap around
            if self.ui.renderer.selected_custom_diamond_index >= len(self.ui.renderer.custom_diamonds):
                self.ui.renderer.selected_custom_diamond_index = 0
            elif self.ui.renderer.selected_custom_diamond_index < 0:
                self.ui.renderer.selected_custom_diamond_index = len(self.ui.renderer.custom_diamonds) - 1
        
        # Update selected diamond
        if 0 <= self.ui.renderer.selected_custom_diamond_index < len(self.ui.renderer.custom_diamonds):
            self.ui.renderer.selected_diamond = self.ui.renderer.custom_diamonds[self.ui.renderer.selected_custom_diamond_index]
            print(f"Selected custom diamond: {self.ui.renderer.selected_diamond}")
        
        # Clear cache and update display
        self.ui.renderer._clear_sprite_display_cache()
        self._update_vertex_info_label()
    
    def _update_custom_diamonds_list(self):
        """Update the renderer's custom diamonds list based on current sprite"""
        if not self.ui.model:
            self.ui.renderer.custom_diamonds = []
            return
        
        current_sprite = self.ui.model.get_current_sprite()
        if not current_sprite or not current_sprite.diamond_info:
            self.ui.renderer.custom_diamonds = []
            return
        
        # Update list of custom diamond names
        self.ui.renderer.custom_diamonds = list(current_sprite.diamond_info.extra_diamonds.keys())
        
        # Validate selected index
        if (self.ui.renderer.selected_custom_diamond_index >= len(self.ui.renderer.custom_diamonds) or
            self.ui.renderer.selected_custom_diamond_index < 0):
            self.ui.renderer.selected_custom_diamond_index = -1
            # Reset to lower diamond if custom selection is invalid
            if self.ui.renderer.selected_diamond not in ['lower', 'upper'] and self.ui.renderer.selected_diamond not in self.ui.renderer.custom_diamonds:
                self.ui.renderer.selected_diamond = 'lower'
    
    def _show_diamond_name_dialog(self):
        """Show a dialog to get the name for a new custom diamond"""
        try:
            import tkinter as tk
            from tkinter import simpledialog
            
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            # Show input dialog
            diamond_name = simpledialog.askstring(
                "Custom Diamond",
                "Enter name for the new custom diamond:",
                initialvalue="custom_diamond"
            )
            
            root.destroy()
            return diamond_name
            
        except Exception as e:
            print(f"Error showing diamond name dialog: {e}")
            return None
    
    def _sync_complete_custom_diamond_to_model(self, sprite_key: int, diamond_name: str):
        """Sync a complete diamond from manual vertices to the model (works for lower, upper, and custom diamonds)"""
        # Check if we have manual vertices for this diamond
        manual_data = self.ui.renderer.manual_vertices.get(sprite_key, {})
        diamond_vertices = manual_data.get(diamond_name, {})
        
        # Check if the diamond is complete (has all 4 vertices)
        required_vertices = ['north', 'south', 'east', 'west']
        if not all(vertex in diamond_vertices for vertex in required_vertices):
            print(f"Diamond '{diamond_name}' is not complete yet ({len(diamond_vertices)}/4 vertices)")
            return
        
        current_sprite = self.ui.model.get_current_sprite()
        if not current_sprite:
            return
        
        # Ensure diamond_info exists
        if not current_sprite.diamond_info:
            print(f"No diamond_info available for sprite {sprite_key}")
            return
        
        from spritesheet_model import Point, GameplayDiamondData
        
        # Helper function to update diamond vertices and recalculate derived properties
        def update_diamond_vertices(diamond_data):
            diamond_data.north_vertex = Point(x=diamond_vertices['north'][0], y=diamond_vertices['north'][1])
            diamond_data.south_vertex = Point(x=diamond_vertices['south'][0], y=diamond_vertices['south'][1])
            diamond_data.east_vertex = Point(x=diamond_vertices['east'][0], y=diamond_vertices['east'][1])
            diamond_data.west_vertex = Point(x=diamond_vertices['west'][0], y=diamond_vertices['west'][1])
            
            # Recalculate center
            diamond_data.center = Point(
                x=(diamond_data.north_vertex.x + diamond_data.south_vertex.x) // 2,
                y=(diamond_data.north_vertex.y + diamond_data.south_vertex.y) // 2
            )
            
            # Recalculate midpoints
            diamond_data.north_east_midpoint = Point(
                x=(diamond_data.north_vertex.x + diamond_data.east_vertex.x) // 2,
                y=(diamond_data.north_vertex.y + diamond_data.east_vertex.y) // 2
            )
            diamond_data.east_south_midpoint = Point(
                x=(diamond_data.east_vertex.x + diamond_data.south_vertex.x) // 2,
                y=(diamond_data.east_vertex.y + diamond_data.south_vertex.y) // 2
            )
            diamond_data.south_west_midpoint = Point(
                x=(diamond_data.south_vertex.x + diamond_data.west_vertex.x) // 2,
                y=(diamond_data.south_vertex.y + diamond_data.west_vertex.y) // 2
            )
            diamond_data.west_north_midpoint = Point(
                x=(diamond_data.west_vertex.x + diamond_data.north_vertex.x) // 2,
                y=(diamond_data.west_vertex.y + diamond_data.north_vertex.y) // 2
            )
            
            # Force recalculation of sub-diamonds with new vertex positions
            # Clear existing sub-diamonds first to force recalculation
            diamond_data.sub_diamonds = {}
            diamond_data.ensure_sub_diamonds_initialized()
        
        # Handle lower diamond
        if diamond_name == 'lower':
            if current_sprite.diamond_info.lower_diamond:
                print(f"Updating lower diamond vertices from manual input")
                update_diamond_vertices(current_sprite.diamond_info.lower_diamond)
                
                # Update z_offset (lower diamond always has z_offset = 0)
                current_sprite.diamond_info.lower_diamond.z_offset = 0.0
                print(f"Lower diamond updated and ready for sub-diamond mode")
            else:
                print(f"No lower diamond exists in model to update")
                
        # Handle upper diamond
        elif diamond_name == 'upper':
            if current_sprite.diamond_info.upper_diamond:
                print(f"Updating upper diamond vertices from manual input")
                update_diamond_vertices(current_sprite.diamond_info.upper_diamond)
                
                # Recalculate z_offset relative to lower diamond
                if current_sprite.diamond_info.lower_diamond:
                    lower_north_y = current_sprite.diamond_info.lower_diamond.north_vertex.y
                    upper_z_offset = float(lower_north_y - diamond_vertices['north'][1])
                    current_sprite.diamond_info.upper_diamond.z_offset = upper_z_offset
                    print(f"Upper diamond updated with z_offset {upper_z_offset} and ready for sub-diamond mode")
                else:
                    current_sprite.diamond_info.upper_diamond.z_offset = 0.0
                    print(f"Upper diamond updated (no lower diamond for z_offset calculation)")
            else:
                print(f"No upper diamond exists in model to update")
                
        # Handle custom diamonds
        else:
            if diamond_name in current_sprite.diamond_info.extra_diamonds:
                print(f"Updating custom diamond '{diamond_name}' vertices from manual input")
                update_diamond_vertices(current_sprite.diamond_info.extra_diamonds[diamond_name])
                
                # Recalculate z_offset relative to lower diamond
                if current_sprite.diamond_info.lower_diamond:
                    lower_north_y = current_sprite.diamond_info.lower_diamond.north_vertex.y
                    custom_z_offset = float(lower_north_y - diamond_vertices['north'][1])
                    current_sprite.diamond_info.extra_diamonds[diamond_name].z_offset = custom_z_offset
                    print(f"Custom diamond '{diamond_name}' updated with z_offset {custom_z_offset} and ready for sub-diamond mode")
                else:
                    current_sprite.diamond_info.extra_diamonds[diamond_name].z_offset = 0.0
                    print(f"Custom diamond '{diamond_name}' updated (no lower diamond for z_offset calculation)")
            else:
                # Create new custom diamond in the model
                print(f"Creating new custom diamond '{diamond_name}' in model from complete manual vertices")
                
                # Calculate z_offset relative to lower diamond
                lower_north_y = current_sprite.diamond_info.lower_diamond.north_vertex.y if current_sprite.diamond_info.lower_diamond else 0
                custom_z_offset = float(lower_north_y - diamond_vertices['north'][1])
                
                # Create the new diamond
                new_diamond = GameplayDiamondData(
                    north_vertex=Point(x=diamond_vertices['north'][0], y=diamond_vertices['north'][1]),
                    south_vertex=Point(x=diamond_vertices['south'][0], y=diamond_vertices['south'][1]),
                    east_vertex=Point(x=diamond_vertices['east'][0], y=diamond_vertices['east'][1]),
                    west_vertex=Point(x=diamond_vertices['west'][0], y=diamond_vertices['west'][1]),
                    center=Point(
                        x=(diamond_vertices['north'][0] + diamond_vertices['south'][0]) // 2,
                        y=(diamond_vertices['north'][1] + diamond_vertices['south'][1]) // 2
                    ),
                    z_offset=custom_z_offset
                )
                
                # Use the helper function to set midpoints and initialize sub-diamonds
                update_diamond_vertices(new_diamond)
                
                # Add to model
                current_sprite.diamond_info.extra_diamonds[diamond_name] = new_diamond
                
                # Update renderer's custom diamonds list
                self._update_custom_diamonds_list()
                
                print(f"Custom diamond '{diamond_name}' created in model with z_offset {custom_z_offset}")
                print(f"Diamond is now available for sub-diamond mode and other features")
        
        # Recalculate diamonds_z_offset if both lower and upper diamonds exist
        if (current_sprite.diamond_info.lower_diamond and
            current_sprite.diamond_info.upper_diamond):
            lower_north_y = current_sprite.diamond_info.lower_diamond.north_vertex.y
            upper_north_y = current_sprite.diamond_info.upper_diamond.north_vertex.y
            current_sprite.diamond_info.diamonds_z_offset = float(lower_north_y - upper_north_y)
            print(f"Recalculated diamonds_z_offset: {current_sprite.diamond_info.diamonds_z_offset}")
    
    def handle_sub_diamond_keys(self, key):
        """Handle keyboard input for sub-diamond editing mode"""
        
        # Don't handle sub-diamond keys if manual vertex mode is active
        if self.ui.renderer.manual_vertex_mode:
            return False
        
        # F1/F2 for diamond layer selection and enabling sub-diamond mode (only if not in manual vertex mode)
        if key == pygame.K_F1:
            self.ui.renderer.selected_sub_diamond_layer = 'lower'
            self.ui.renderer.sub_diamond_mode = True
            self.ui.renderer.show_sub_diamonds = True
            self.ui.analysis_controls_panel.components['sub_diamond_mode_button'].set_text('Sub-Diamond Mode: ON')
            print(f"Sub-diamond mode: ON - Layer: LOWER - Mode: {self.ui.renderer.sub_diamond_editing_mode}")
            self.ui.renderer._clear_sprite_display_cache()
            return True
        elif key == pygame.K_F2:
            self.ui.renderer.selected_sub_diamond_layer = 'upper'
            self.ui.renderer.sub_diamond_mode = True
            self.ui.renderer.show_sub_diamonds = True
            self.ui.analysis_controls_panel.components['sub_diamond_mode_button'].set_text('Sub-Diamond Mode: ON')
            print(f"Sub-diamond mode: ON - Layer: UPPER - Mode: {self.ui.renderer.sub_diamond_editing_mode}")
            self.ui.renderer._clear_sprite_display_cache()
            return True
        
        # F3 for cycling through custom diamond layers if in sub-diamond mode
        elif key == pygame.K_F3 and self.ui.renderer.sub_diamond_mode:
            if not self.ui.model:
                return True
            
            current_sprite = self.ui.model.get_current_sprite()
            if not current_sprite or not current_sprite.diamond_info:
                return True
            
            # Get available layers: lower, upper, custom diamonds
            available_layers = ['lower']
            if current_sprite.diamond_info.upper_diamond:
                available_layers.append('upper')
            if current_sprite.diamond_info.extra_diamonds:
                available_layers.extend(current_sprite.diamond_info.extra_diamonds.keys())
            
            # Cycle to next layer
            try:
                current_index = available_layers.index(self.ui.renderer.selected_sub_diamond_layer)
                next_index = (current_index + 1) % len(available_layers)
                self.ui.renderer.selected_sub_diamond_layer = available_layers[next_index]
                print(f"Sub-diamond layer: {self.ui.renderer.selected_sub_diamond_layer.upper()}")
                self.ui.renderer._clear_sprite_display_cache()
            except ValueError:
                # Current layer not found, default to lower
                self.ui.renderer.selected_sub_diamond_layer = 'lower'
            
            return True
        
        # 1/2/3 keys for editing mode selection
        elif key == pygame.K_1:
            self.ui.renderer.sub_diamond_editing_mode = 'surface'
            if not self.ui.renderer.sub_diamond_mode:
                self.ui.renderer.sub_diamond_mode = True
                self.ui.renderer.show_sub_diamonds = True
            print(f"Sub-diamond editing mode: SURFACE (walkability)")
            self.ui.renderer._clear_sprite_display_cache()
            return True
        elif key == pygame.K_2:
            self.ui.renderer.sub_diamond_editing_mode = 'edge_line_of_sight'
            if not self.ui.renderer.sub_diamond_mode:
                self.ui.renderer.sub_diamond_mode = True
                self.ui.renderer.show_sub_diamonds = True
            print(f"Sub-diamond editing mode: EDGE LINE OF SIGHT")
            self.ui.renderer._clear_sprite_display_cache()
            return True
        elif key == pygame.K_3:
            self.ui.renderer.sub_diamond_editing_mode = 'edge_movement'
            if not self.ui.renderer.sub_diamond_mode:
                self.ui.renderer.sub_diamond_mode = True
                self.ui.renderer.show_sub_diamonds = True
            print(f"Sub-diamond editing mode: EDGE MOVEMENT")
            self.ui.renderer._clear_sprite_display_cache()
            return True
        elif key == pygame.K_4:
            self.ui.renderer.sub_diamond_editing_mode = 'z_portal'
            if not self.ui.renderer.sub_diamond_mode:
                self.ui.renderer.sub_diamond_mode = True
                self.ui.renderer.show_sub_diamonds = True
            print(f"Sub-diamond editing mode: Z-PORTAL")
            self.ui.renderer._clear_sprite_display_cache()
            return True
        
        return False
    
    def handle_sub_diamond_click(self, event):
        """Handle mouse clicks for sub-diamond property editing with proper pixeloid coordinate transformation"""
        if not self.ui.renderer.sub_diamond_mode or not self.ui.model:
            return False
        
        mouse_x, mouse_y = event.pos
        drawing_area = pygame.Rect(self.LEFT_PANEL_WIDTH, 0, self.DRAWING_AREA_WIDTH, self.DRAWING_AREA_HEIGHT)
        
        if not drawing_area.collidepoint(mouse_x, mouse_y):
            return False
        
        current_sprite = self.ui.model.get_current_sprite()
        if not current_sprite or not current_sprite.diamond_info:
            return False
        
        # Get the selected diamond data
        diamond_data = None
        if self.ui.renderer.selected_sub_diamond_layer == 'lower' and current_sprite.diamond_info.lower_diamond:
            diamond_data = current_sprite.diamond_info.lower_diamond
        elif self.ui.renderer.selected_sub_diamond_layer == 'upper' and current_sprite.diamond_info.upper_diamond:
            diamond_data = current_sprite.diamond_info.upper_diamond
        elif self.ui.renderer.selected_sub_diamond_layer in current_sprite.diamond_info.extra_diamonds:
            diamond_data = current_sprite.diamond_info.extra_diamonds[self.ui.renderer.selected_sub_diamond_layer]
        
        if not diamond_data or not hasattr(diamond_data, 'sub_diamonds'):
            return False
        
        # Ensure sub-diamonds are initialized
        diamond_data.ensure_sub_diamonds_initialized()
        
        if not diamond_data.sub_diamonds:
            return False
        
        # Convert mouse position to sprite pixel coordinates using proper pixeloid transformation
        sprite_pixel_x, sprite_pixel_y = self._convert_mouse_to_sprite_pixel_coords(event.pos, current_sprite)
        
        print(f"DEBUG SUB-DIAMOND CLICK: Mouse ({mouse_x}, {mouse_y}) -> Sprite pixel ({sprite_pixel_x:.1f}, {sprite_pixel_y:.1f})")
        
        # Handle click based on editing mode
        if self.ui.renderer.sub_diamond_editing_mode == 'surface':
            clicked_element = self._find_sub_diamond_surface_at_position(sprite_pixel_x, sprite_pixel_y, diamond_data.sub_diamonds)
            if clicked_element:
                direction, sub_diamond = clicked_element
                self._toggle_sub_diamond_walkability(sub_diamond, event.button, direction)
                self.ui.renderer._clear_sprite_display_cache()
                self.ui.update_sprite_info()
                return True
        
        elif self.ui.renderer.sub_diamond_editing_mode in ['edge_line_of_sight', 'edge_movement', 'z_portal']:
            clicked_element = self._find_sub_diamond_edge_at_position(sprite_pixel_x, sprite_pixel_y, diamond_data.sub_diamonds)
            if clicked_element:
                edge_info = clicked_element
                if self.ui.renderer.sub_diamond_editing_mode == 'z_portal':
                    self._handle_z_portal_click(edge_info, event.button)
                else:
                    self._handle_edge_click(edge_info, event.button)
                self.ui.renderer._clear_sprite_display_cache()
                self.ui.update_sprite_info()
                return True
        
        return False
    
    def _convert_mouse_to_sprite_pixel_coords(self, mouse_pos, current_sprite):
        """Convert mouse position to sprite pixel coordinates using proper pixeloid transformation"""
        mouse_x, mouse_y = mouse_pos
        mouse_x_in_drawing = mouse_x - self.LEFT_PANEL_WIDTH
        mouse_y_in_drawing = mouse_y
        
        # Calculate expanded bounds if diamond extends beyond bbox
        expanded_bounds = self.ui.renderer._calculate_expanded_bounds(current_sprite, self.ui.model)
        
        sprite_rect = pygame.Rect(0, 0, current_sprite.original_size[0], current_sprite.original_size[1])
        
        if expanded_bounds and expanded_bounds['diamond_extends']:
            # Use expanded bounds for positioning calculations
            expanded_display_width = expanded_bounds['width'] * self.ui.model.pixeloid_multiplier
            expanded_display_height = expanded_bounds['height'] * self.ui.model.pixeloid_multiplier
            
            # Center the expanded area
            base_expanded_x = (self.DRAWING_AREA_WIDTH - expanded_display_width) // 2
            base_expanded_y = (self.DRAWING_AREA_HEIGHT - expanded_display_height) // 2
            
            # Calculate sprite offset within expanded area
            bbox_offset_x = (expanded_bounds['original_bbox'].x - expanded_bounds['x']) * self.ui.model.pixeloid_multiplier
            bbox_offset_y = (expanded_bounds['original_bbox'].y - expanded_bounds['y']) * self.ui.model.pixeloid_multiplier
            
            sprite_x = base_expanded_x + bbox_offset_x + self.ui.model.pan_x
            sprite_y = base_expanded_y + bbox_offset_y + self.ui.model.pan_y
        else:
            # Use original positioning logic
            display_width = sprite_rect.width * self.ui.model.pixeloid_multiplier
            display_height = sprite_rect.height * self.ui.model.pixeloid_multiplier
            base_sprite_x = (self.DRAWING_AREA_WIDTH - display_width) // 2
            base_sprite_y = (self.DRAWING_AREA_HEIGHT - display_height) // 2
            sprite_x = base_sprite_x + self.ui.model.pan_x
            sprite_y = base_sprite_y + self.ui.model.pan_y
        
        # Calculate which sprite pixel is under the mouse
        sprite_pixel_x = (mouse_x_in_drawing - sprite_x) / self.ui.model.pixeloid_multiplier
        sprite_pixel_y = (mouse_y_in_drawing - sprite_y) / self.ui.model.pixeloid_multiplier
        
        return sprite_pixel_x, sprite_pixel_y
    
    def _find_sub_diamond_surface_at_position(self, x, y, sub_diamonds):
        """Find which sub-diamond surface contains the given position"""
        for direction, sub_diamond in sub_diamonds.items():
            if self._point_in_sub_diamond_surface(x, y, sub_diamond):
                return (direction, sub_diamond)
        return None
    
    def _find_sub_diamond_edge_at_position(self, x, y, sub_diamonds):
        """Find which sub-diamond edge is closest to the given position"""
        closest_edge = None
        closest_distance = float('inf')
        edge_detection_threshold = 3.0  # pixels
        
        for direction, sub_diamond in sub_diamonds.items():
            # Check each edge of this sub-diamond
            edges = [
                ('north_west_edge', sub_diamond.north_vertex, sub_diamond.west_vertex),
                ('north_east_edge', sub_diamond.north_vertex, sub_diamond.east_vertex),
                ('south_west_edge', sub_diamond.south_vertex, sub_diamond.west_vertex),
                ('south_east_edge', sub_diamond.south_vertex, sub_diamond.east_vertex)
            ]
            
            for edge_name, start_vertex, end_vertex in edges:
                distance = self._point_to_line_distance(x, y, start_vertex, end_vertex)
                if distance < edge_detection_threshold and distance < closest_distance:
                    closest_distance = distance
                    edge_props = getattr(sub_diamond, edge_name, None)
                    if edge_props:
                        closest_edge = {
                            'sub_diamond': sub_diamond,
                            'direction': direction,
                            'edge_name': edge_name,
                            'edge_props': edge_props,
                            'start_vertex': start_vertex,
                            'end_vertex': end_vertex
                        }
        
        return closest_edge
    
    def _handle_edge_click(self, edge_info, mouse_button):
        """Handle click on a sub-diamond edge"""
        edge_props = edge_info['edge_props']
        direction = edge_info['direction']
        edge_name = edge_info['edge_name']
        
        if self.ui.renderer.sub_diamond_editing_mode == 'edge_line_of_sight':
            if mouse_button == 1:  # Left click - toggle true/false
                if edge_props.blocks_line_of_sight is None:
                    edge_props.blocks_line_of_sight = True
                elif edge_props.blocks_line_of_sight:
                    edge_props.blocks_line_of_sight = False
                else:
                    edge_props.blocks_line_of_sight = True
                print(f"Sub-diamond {direction} {edge_name} blocks line of sight: {edge_props.blocks_line_of_sight}")
            elif mouse_button == 3:  # Right click - set to None
                edge_props.blocks_line_of_sight = None
                print(f"Sub-diamond {direction} {edge_name} blocks line of sight: None")
        
        elif self.ui.renderer.sub_diamond_editing_mode == 'edge_movement':
            if mouse_button == 1:  # Left click - toggle true/false
                if edge_props.blocks_movement is None:
                    edge_props.blocks_movement = True
                elif edge_props.blocks_movement:
                    edge_props.blocks_movement = False
                else:
                    edge_props.blocks_movement = True
                print(f"Sub-diamond {direction} {edge_name} blocks movement: {edge_props.blocks_movement}")
            elif mouse_button == 3:  # Right click - set to None
                edge_props.blocks_movement = None
                print(f"Sub-diamond {direction} {edge_name} blocks movement: None")
        
        # Handle shared edges - find adjacent sub-diamonds that share this edge
        self._update_shared_edges(edge_info)
    
    def _find_sub_diamond_at_position(self, x, y, sub_diamonds):
        """Find which sub-diamond contains the given position"""
        for direction, sub_diamond in sub_diamonds.items():
            if self._point_in_sub_diamond(x, y, sub_diamond):
                return (direction, sub_diamond)
        return None
    
    def _point_in_sub_diamond_surface(self, x, y, sub_diamond):
        """Check if a point is inside a sub-diamond surface using proper diamond geometry"""
        return self._point_in_diamond_shape(x, y,
                                          sub_diamond.north_vertex, sub_diamond.south_vertex,
                                          sub_diamond.east_vertex, sub_diamond.west_vertex)
    
    def _point_in_diamond_shape(self, x, y, north_vertex, south_vertex, east_vertex, west_vertex):
        """Check if a point is inside a diamond shape using cross product method"""
        # Convert vertices to float for precise calculations
        n_x, n_y = float(north_vertex.x), float(north_vertex.y)
        s_x, s_y = float(south_vertex.x), float(south_vertex.y)
        e_x, e_y = float(east_vertex.x), float(east_vertex.y)
        w_x, w_y = float(west_vertex.x), float(west_vertex.y)
        
        # Check if point is on the same side of each edge
        def cross_product_sign(ax, ay, bx, by, px, py):
            return (bx - ax) * (py - ay) - (by - ay) * (px - ax)
        
        # Check each edge of the diamond (clockwise order: N->E->S->W->N)
        sign1 = cross_product_sign(n_x, n_y, e_x, e_y, x, y)  # North to East
        sign2 = cross_product_sign(e_x, e_y, s_x, s_y, x, y)  # East to South
        sign3 = cross_product_sign(s_x, s_y, w_x, w_y, x, y)  # South to West
        sign4 = cross_product_sign(w_x, w_y, n_x, n_y, x, y)  # West to North
        
        # Point is inside if all cross products have the same sign (all positive or all negative)
        return (sign1 >= 0 and sign2 >= 0 and sign3 >= 0 and sign4 >= 0) or \
               (sign1 <= 0 and sign2 <= 0 and sign3 <= 0 and sign4 <= 0)
    
    def _point_to_line_distance(self, x, y, start_vertex, end_vertex):
        """Calculate the shortest distance from a point to a line segment"""
        x1, y1 = float(start_vertex.x), float(start_vertex.y)
        x2, y2 = float(end_vertex.x), float(end_vertex.y)
        px, py = float(x), float(y)
        
        # Vector from start to end
        dx = x2 - x1
        dy = y2 - y1
        
        # If the line segment is actually a point
        if dx == 0 and dy == 0:
            return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
        
        # Calculate the parameter t for the closest point on the line
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        
        # Find the closest point on the line segment
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        # Calculate distance to the closest point
        return ((px - closest_x) ** 2 + (py - closest_y) ** 2) ** 0.5
    
    def _update_shared_edges(self, edge_info):
        """Update shared edges between adjacent sub-diamonds"""
        # Get the current sub-diamond and edge information
        current_sub_diamond = edge_info['sub_diamond']
        current_direction = edge_info['direction']
        edge_name = edge_info['edge_name']
        edge_props = edge_info['edge_props']
        
        # Find the parent diamond to access all sub-diamonds
        current_sprite = self.ui.model.get_current_sprite()
        if not current_sprite or not current_sprite.diamond_info:
            return
        
        # Get the selected diamond data
        diamond_data = None
        if self.ui.renderer.selected_sub_diamond_layer == 'lower' and current_sprite.diamond_info.lower_diamond:
            diamond_data = current_sprite.diamond_info.lower_diamond
        elif self.ui.renderer.selected_sub_diamond_layer == 'upper' and current_sprite.diamond_info.upper_diamond:
            diamond_data = current_sprite.diamond_info.upper_diamond
        elif self.ui.renderer.selected_sub_diamond_layer in current_sprite.diamond_info.extra_diamonds:
            diamond_data = current_sprite.diamond_info.extra_diamonds[self.ui.renderer.selected_sub_diamond_layer]
        
        if not diamond_data or not diamond_data.sub_diamonds:
            return
        
        # Define which edges are shared between adjacent sub-diamonds
        # Based on the correct topology: N-W, N-E, S-W, S-E borders
        shared_edge_mappings = {
            # North and West share: N's south_west with W's north_east
            ('north', 'south_west_edge'): ('west', 'north_east_edge'),
            ('west', 'north_east_edge'): ('north', 'south_west_edge'),
            
            # North and East share: N's south_east with E's north_west
            ('north', 'south_east_edge'): ('east', 'north_west_edge'),
            ('east', 'north_west_edge'): ('north', 'south_east_edge'),
            
            # South and West share: S's north_west with W's south_east
            ('south', 'north_west_edge'): ('west', 'south_east_edge'),
            ('west', 'south_east_edge'): ('south', 'north_west_edge'),
            
            # South and East share: S's north_east with E's south_west
            ('south', 'north_east_edge'): ('east', 'south_west_edge'),
            ('east', 'south_west_edge'): ('south', 'north_east_edge'),
        }
        
        # Find the corresponding shared edge
        key = (current_direction, edge_name)
        if key in shared_edge_mappings:
            target_direction, target_edge_name = shared_edge_mappings[key]
            
            # Check if the target sub-diamond exists
            if target_direction in diamond_data.sub_diamonds:
                target_sub_diamond = diamond_data.sub_diamonds[target_direction]
                target_edge_props = getattr(target_sub_diamond, target_edge_name, None)
                
                if target_edge_props:
                    # Copy the properties to the shared edge
                    target_edge_props.blocks_line_of_sight = edge_props.blocks_line_of_sight
                    target_edge_props.blocks_movement = edge_props.blocks_movement
                    
                    print(f"Updated shared edge: {target_direction} {target_edge_name} = {current_direction} {edge_name}")
                    print(f"  Line of sight: {edge_props.blocks_line_of_sight}")
                    print(f"  Movement: {edge_props.blocks_movement}")
                else:
                    print(f"ERROR: Could not find target edge {target_direction}.{target_edge_name}")
            else:
                print(f"ERROR: Target sub-diamond {target_direction} not found")
        else:
            print(f"No shared edge mapping found for {current_direction}.{edge_name}")
    
    def _point_in_sub_diamond(self, x, y, sub_diamond):
        """Check if a point is inside a sub-diamond using simple bounds check"""
        # Get sub-diamond bounds
        vertices = [
            (sub_diamond.north_vertex.x, sub_diamond.north_vertex.y),
            (sub_diamond.south_vertex.x, sub_diamond.south_vertex.y),
            (sub_diamond.east_vertex.x, sub_diamond.east_vertex.y),
            (sub_diamond.west_vertex.x, sub_diamond.west_vertex.y)
        ]
        
        # Simple bounding box check first
        min_x = min(v[0] for v in vertices)
        max_x = max(v[0] for v in vertices)
        min_y = min(v[1] for v in vertices)
        max_y = max(v[1] for v in vertices)
        
        return min_x <= x <= max_x and min_y <= y <= max_y
    
    def _toggle_sub_diamond_walkability(self, sub_diamond, mouse_button, direction):
        """Toggle walkability property based on mouse button"""
        if mouse_button == 1:  # Left click - toggle true/false
            if sub_diamond.is_walkable is None:
                sub_diamond.is_walkable = True
            elif sub_diamond.is_walkable:
                sub_diamond.is_walkable = False
            else:
                sub_diamond.is_walkable = True
            print(f"Sub-diamond {direction} surface walkability: {sub_diamond.is_walkable}")
        elif mouse_button == 3:  # Right click - set to None
            sub_diamond.is_walkable = None
            print(f"Sub-diamond {direction} surface walkability: None")
    
    def _toggle_sub_diamond_line_of_sight(self, sub_diamond, mouse_button, direction):
        """Legacy method - Toggle line of sight properties for all edges"""
        if mouse_button == 1:  # Left click - toggle true/false for all edges
            current_value = getattr(sub_diamond.north_west_edge, 'blocks_line_of_sight', None)
            new_value = not (current_value or False) if current_value is not None else True
            self._set_all_edge_line_of_sight(sub_diamond, new_value)
            print(f"Sub-diamond {direction} blocks line of sight (all edges): {new_value}")
        elif mouse_button == 3:  # Right click - set to None for all edges
            self._set_all_edge_line_of_sight(sub_diamond, None)
            print(f"Sub-diamond {direction} blocks line of sight (all edges): None")
    
    def _set_all_edge_line_of_sight(self, sub_diamond, value):
        """Set line of sight blocking for all edges of a sub-diamond"""
        for edge_attr in ['north_west_edge', 'north_east_edge', 'south_west_edge', 'south_east_edge']:
            edge = getattr(sub_diamond, edge_attr, None)
            if edge:
                edge.blocks_line_of_sight = value
    
    def handle_sub_diamond_set_default(self):
        """Set default sub-diamond properties based on diamond layer: Upper=allow all, Lower=block all"""
        if not self.ui.model or not self.ui.renderer.sub_diamond_mode:
            print("Sub-diamond mode must be active to set defaults")
            return
        
        current_sprite = self.ui.model.get_current_sprite()
        if not current_sprite or not current_sprite.diamond_info:
            return
        
        # Get the selected diamond data
        diamond_data = None
        layer_name = self.ui.renderer.selected_sub_diamond_layer
        if layer_name == 'lower' and current_sprite.diamond_info.lower_diamond:
            diamond_data = current_sprite.diamond_info.lower_diamond
        elif layer_name == 'upper' and current_sprite.diamond_info.upper_diamond:
            diamond_data = current_sprite.diamond_info.upper_diamond
        elif layer_name in current_sprite.diamond_info.extra_diamonds:
            diamond_data = current_sprite.diamond_info.extra_diamonds[layer_name]
        
        if not diamond_data or not hasattr(diamond_data, 'sub_diamonds'):
            return
        
        # Ensure sub-diamonds are initialized
        diamond_data.ensure_sub_diamonds_initialized()
        
        if not diamond_data.sub_diamonds:
            return
        
        print(f"\n=== SETTING DEFAULT SUB-DIAMOND PROPERTIES FOR {layer_name.upper()} LAYER ===")
        
        # Determine default values based on diamond layer
        if layer_name == 'upper':
            # Upper diamond: all quadrants walkable, all edges allow passage
            default_walkable = True
            default_blocking = False
            print("Upper diamond defaults: ALL QUADRANTS WALKABLE, ALL EDGES ALLOW")
        else:
            # Lower diamond (and custom diamonds): all quadrants not walkable, all edges block
            default_walkable = False
            default_blocking = True
            print("Lower diamond defaults: ALL QUADRANTS NOT WALKABLE, ALL EDGES BLOCK")
        
        # Set properties for all quadrants
        for direction, sub_diamond in diamond_data.sub_diamonds.items():
            # Set walkability
            sub_diamond.is_walkable = default_walkable
            
            # Set all edge properties for this sub-diamond
            for edge_attr in ['north_west_edge', 'north_east_edge', 'south_west_edge', 'south_east_edge']:
                edge = getattr(sub_diamond, edge_attr, None)
                if edge:
                    edge.blocks_line_of_sight = default_blocking
                    edge.blocks_movement = default_blocking
            
            print(f"{direction.title()} quadrant: {'WALKABLE' if default_walkable else 'NOT WALKABLE'}, {'ALLOWS ALL' if not default_blocking else 'BLOCKS ALL'}")
        
        # Update shared edges to maintain consistency
        self._update_all_shared_edges(diamond_data.sub_diamonds)
        
        # Clear cache and update display
        self.ui.renderer._clear_sprite_display_cache()
        self.ui.update_sprite_info()
        
        print("Default sub-diamond properties applied successfully")
    
    def handle_sub_diamond_clear_all(self):
        """Clear all sub-diamond properties to None (unset state)"""
        if not self.ui.model or not self.ui.renderer.sub_diamond_mode:
            print("Sub-diamond mode must be active to clear properties")
            return
        
        current_sprite = self.ui.model.get_current_sprite()
        if not current_sprite or not current_sprite.diamond_info:
            return
        
        # Get the selected diamond data
        diamond_data = None
        layer_name = self.ui.renderer.selected_sub_diamond_layer
        if layer_name == 'lower' and current_sprite.diamond_info.lower_diamond:
            diamond_data = current_sprite.diamond_info.lower_diamond
        elif layer_name == 'upper' and current_sprite.diamond_info.upper_diamond:
            diamond_data = current_sprite.diamond_info.upper_diamond
        elif layer_name in current_sprite.diamond_info.extra_diamonds:
            diamond_data = current_sprite.diamond_info.extra_diamonds[layer_name]
        
        if not diamond_data or not hasattr(diamond_data, 'sub_diamonds'):
            return
        
        # Ensure sub-diamonds are initialized
        diamond_data.ensure_sub_diamonds_initialized()
        
        if not diamond_data.sub_diamonds:
            return
        
        print(f"\n=== CLEARING ALL SUB-DIAMOND PROPERTIES FOR {layer_name.upper()} LAYER ===")
        
        # Clear properties for each quadrant
        for direction, sub_diamond in diamond_data.sub_diamonds.items():
            # Clear walkability
            sub_diamond.is_walkable = None
            
            # Clear all edge properties for this sub-diamond
            for edge_attr in ['north_west_edge', 'north_east_edge', 'south_west_edge', 'south_east_edge']:
                edge = getattr(sub_diamond, edge_attr, None)
                if edge:
                    edge.blocks_line_of_sight = None
                    edge.blocks_movement = None
            
            print(f"{direction.title()} quadrant: ALL PROPERTIES CLEARED")
        
        # Clear cache and update display
        self.ui.renderer._clear_sprite_display_cache()
        self.ui.update_sprite_info()
        
        print("All sub-diamond properties cleared successfully")
    
    def _update_all_shared_edges(self, sub_diamonds):
        """Update all shared edges to maintain consistency between adjacent sub-diamonds"""
        # Define which edges are shared between adjacent sub-diamonds
        shared_edge_mappings = {
            # North and West share: N's south_west with W's north_east
            ('north', 'south_west_edge'): ('west', 'north_east_edge'),
            ('west', 'north_east_edge'): ('north', 'south_west_edge'),
            
            # North and East share: N's south_east with E's north_west
            ('north', 'south_east_edge'): ('east', 'north_west_edge'),
            ('east', 'north_west_edge'): ('north', 'south_east_edge'),
            
            # South and West share: S's north_west with W's south_east
            ('south', 'north_west_edge'): ('west', 'south_east_edge'),
            ('west', 'south_east_edge'): ('south', 'north_west_edge'),
            
            # South and East share: S's north_east with E's south_west
            ('south', 'north_east_edge'): ('east', 'south_west_edge'),
            ('east', 'south_west_edge'): ('south', 'north_east_edge'),
        }
        
        # Process each mapping to synchronize shared edges
        processed_pairs = set()
        
        for (source_direction, source_edge_name), (target_direction, target_edge_name) in shared_edge_mappings.items():
            # Avoid processing the same pair twice
            pair_key = tuple(sorted([(source_direction, source_edge_name), (target_direction, target_edge_name)]))
            if pair_key in processed_pairs:
                continue
            processed_pairs.add(pair_key)
            
            # Check if both sub-diamonds exist
            if source_direction in sub_diamonds and target_direction in sub_diamonds:
                source_sub = sub_diamonds[source_direction]
                target_sub = sub_diamonds[target_direction]
                
                source_edge = getattr(source_sub, source_edge_name, None)
                target_edge = getattr(target_sub, target_edge_name, None)
                
                if source_edge and target_edge:
                    # Synchronize properties (use source as reference)
                    target_edge.blocks_line_of_sight = source_edge.blocks_line_of_sight
                    target_edge.blocks_movement = source_edge.blocks_movement
    
    def handle_sub_diamond_set_all_true(self):
        """Set all sub-diamond properties to True (block everything)"""
        if not self.ui.model or not self.ui.renderer.sub_diamond_mode:
            print("Sub-diamond mode must be active to set all properties")
            return
        
        current_sprite = self.ui.model.get_current_sprite()
        if not current_sprite or not current_sprite.diamond_info:
            return
        
        # Get the selected diamond data
        diamond_data = None
        layer_name = self.ui.renderer.selected_sub_diamond_layer
        if layer_name == 'lower' and current_sprite.diamond_info.lower_diamond:
            diamond_data = current_sprite.diamond_info.lower_diamond
        elif layer_name == 'upper' and current_sprite.diamond_info.upper_diamond:
            diamond_data = current_sprite.diamond_info.upper_diamond
        elif layer_name in current_sprite.diamond_info.extra_diamonds:
            diamond_data = current_sprite.diamond_info.extra_diamonds[layer_name]
        
        if not diamond_data or not hasattr(diamond_data, 'sub_diamonds'):
            return
        
        # Ensure sub-diamonds are initialized
        diamond_data.ensure_sub_diamonds_initialized()
        
        if not diamond_data.sub_diamonds:
            return
        
        print(f"\n=== SETTING ALL PROPERTIES TO BLOCK FOR {layer_name.upper()} LAYER ===")
        
        # Set all properties to True (blocking) for all quadrants
        for direction, sub_diamond in diamond_data.sub_diamonds.items():
            # Set walkability to False (not walkable)
            sub_diamond.is_walkable = False
            
            # Set all edge properties to True (blocking)
            for edge_attr in ['north_west_edge', 'north_east_edge', 'south_west_edge', 'south_east_edge']:
                edge = getattr(sub_diamond, edge_attr, None)
                if edge:
                    edge.blocks_line_of_sight = True
                    edge.blocks_movement = True
            
            print(f"{direction.title()} quadrant: NOT WALKABLE, BLOCKS ALL")
        
        # Update shared edges to maintain consistency
        self._update_all_shared_edges(diamond_data.sub_diamonds)
        
        # Clear cache and update display
        self.ui.renderer._clear_sprite_display_cache()
        self.ui.update_sprite_info()
        
        print("All properties set to block successfully")
    
    def handle_sub_diamond_set_all_false(self):
        """Set all sub-diamond properties to False (allow everything)"""
        if not self.ui.model or not self.ui.renderer.sub_diamond_mode:
            print("Sub-diamond mode must be active to set all properties")
            return
        
        current_sprite = self.ui.model.get_current_sprite()
        if not current_sprite or not current_sprite.diamond_info:
            return
        
        # Get the selected diamond data
        diamond_data = None
        layer_name = self.ui.renderer.selected_sub_diamond_layer
        if layer_name == 'lower' and current_sprite.diamond_info.lower_diamond:
            diamond_data = current_sprite.diamond_info.lower_diamond
        elif layer_name == 'upper' and current_sprite.diamond_info.upper_diamond:
            diamond_data = current_sprite.diamond_info.upper_diamond
        elif layer_name in current_sprite.diamond_info.extra_diamonds:
            diamond_data = current_sprite.diamond_info.extra_diamonds[layer_name]
        
        if not diamond_data or not hasattr(diamond_data, 'sub_diamonds'):
            return
        
        # Ensure sub-diamonds are initialized
        diamond_data.ensure_sub_diamonds_initialized()
        
        if not diamond_data.sub_diamonds:
            return
        
        print(f"\n=== SETTING ALL PROPERTIES TO ALLOW FOR {layer_name.upper()} LAYER ===")
        
        # Set all properties to False (allowing) for all quadrants
        for direction, sub_diamond in diamond_data.sub_diamonds.items():
            # Set walkability to True (walkable)
            sub_diamond.is_walkable = True
            
            # Set all edge properties to False (allowing)
            for edge_attr in ['north_west_edge', 'north_east_edge', 'south_west_edge', 'south_east_edge']:
                edge = getattr(sub_diamond, edge_attr, None)
                if edge:
                    edge.blocks_line_of_sight = False
                    edge.blocks_movement = False
            
            print(f"{direction.title()} quadrant: WALKABLE, ALLOWS ALL")
        
        # Update shared edges to maintain consistency
        self._update_all_shared_edges(diamond_data.sub_diamonds)
        
        # Clear cache and update display
        self.ui.renderer._clear_sprite_display_cache()
        self.ui.update_sprite_info()
        
        print("All properties set to allow successfully")
    
    def _handle_z_portal_click(self, edge_info, mouse_button):
        """Handle click on a sub-diamond edge for z-portal editing"""
        edge_props = edge_info['edge_props']
        direction = edge_info['direction']
        edge_name = edge_info['edge_name']
        
        if mouse_button == 1:  # Left click - set or modify z-portal
            if edge_props.z_portal is None:
                # Create new z-portal - show dialog to select target elevation
                target_elevation = self._show_z_portal_dialog(direction, edge_name)
                if target_elevation is not None:
                    edge_props.z_portal = target_elevation
                    print(f"Created z-portal on {direction} {edge_name} -> elevation {target_elevation}")
                    
                    # Create bi-directional portal on target diamond if possible
                    self._create_bidirectional_portal(edge_info, target_elevation)
                else:
                    print("Z-portal creation cancelled")
            else:
                # Modify existing z-portal
                current_elevation = edge_props.z_portal
                target_elevation = self._show_z_portal_dialog(direction, edge_name, current_elevation)
                if target_elevation is not None:
                    edge_props.z_portal = target_elevation
                    print(f"Modified z-portal on {direction} {edge_name} -> elevation {target_elevation}")
                    
                    # Update bi-directional portal
                    self._create_bidirectional_portal(edge_info, target_elevation)
                else:
                    print("Z-portal modification cancelled")
                    
        elif mouse_button == 3:  # Right click - remove z-portal
            if edge_props.z_portal is not None:
                old_elevation = edge_props.z_portal
                edge_props.z_portal = None
                print(f"Removed z-portal from {direction} {edge_name} (was -> elevation {old_elevation})")
                
                # Remove bi-directional portal if it exists
                self._remove_bidirectional_portal(edge_info, old_elevation)
            else:
                print(f"No z-portal to remove from {direction} {edge_name}")
        
        # Handle shared edges - find adjacent sub-diamonds that share this edge
        self._update_shared_edges(edge_info)
    
    def _show_z_portal_dialog(self, direction, edge_name, current_elevation=None):
        """Show dialog to select target diamond for z-portal"""
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            # Get available target diamonds
            current_sprite = self.ui.model.get_current_sprite()
            if not current_sprite or not current_sprite.diamond_info:
                print("No diamond data available for portal creation")
                return None
            
            diamond_info = current_sprite.diamond_info
            available_diamonds = []
            
            # Get the lower diamond's north vertex Y coordinate for z_offset calculation
            # (same logic as in spritesheet_model.py _export_single_diamond)
            lower_north_y = diamond_info.lower_diamond.north_vertex.y if diamond_info.lower_diamond else 0
            
            # Add lower diamond
            if diamond_info.lower_diamond:
                # Lower diamond always has calculated z_offset = 0.0
                calculated_z_offset = 0.0
                available_diamonds.append(("Lower Diamond", "lower", calculated_z_offset))
            
            # Add upper diamond
            if diamond_info.upper_diamond:
                # Upper diamond z_offset = lower_north_y - upper_north_y
                calculated_z_offset = float(lower_north_y - diamond_info.upper_diamond.north_vertex.y)
                available_diamonds.append(("Upper Diamond", "upper", calculated_z_offset))
            
            # Add custom diamonds
            if diamond_info.extra_diamonds:
                for diamond_name, diamond_data in diamond_info.extra_diamonds.items():
                    # Custom diamond z_offset = lower_north_y - custom_north_y
                    calculated_z_offset = float(lower_north_y - diamond_data.north_vertex.y)
                    display_name = f"Custom: {diamond_name.title()}"
                    available_diamonds.append((display_name, diamond_name, calculated_z_offset))
            
            if len(available_diamonds) <= 1:
                messagebox.showinfo("Z-Portal", "Need at least 2 diamonds to create portals between them.")
                return None
            
            # Remove current layer from options (can't portal to self)
            current_layer = self.ui.renderer.selected_sub_diamond_layer
            available_diamonds = [(display, name, z_offset) for display, name, z_offset in available_diamonds if name != current_layer]
            
            if not available_diamonds:
                messagebox.showinfo("Z-Portal", "No other diamonds available to portal to.")
                return None
            
            # Create selection dialog
            root = tk.Tk()
            root.title(f"Z-Portal: {direction} {edge_name}")
            root.geometry("400x300")
            
            # Center the window
            root.eval('tk::PlaceWindow . center')
            
            selected_z_offset = None
            
            def on_select():
                nonlocal selected_z_offset
                selection = listbox.curselection()
                if selection:
                    index = selection[0]
                    _, _, z_offset = available_diamonds[index]
                    selected_z_offset = z_offset
                    root.destroy()
            
            def on_cancel():
                root.destroy()
            
            # Create UI elements
            tk.Label(root, text=f"Select target diamond for portal:", font=("Arial", 12)).pack(pady=10)
            
            if current_elevation is not None:
                current_diamond_name = "Unknown"
                for display, name, z_offset in available_diamonds + [(f"Current: {current_layer.title()}", current_layer, current_elevation)]:
                    if abs(z_offset - current_elevation) < 0.1:
                        current_diamond_name = display
                        break
                tk.Label(root, text=f"Current target: {current_diamond_name}", font=("Arial", 10), fg="blue").pack(pady=5)
            
            listbox = tk.Listbox(root, font=("Arial", 11), height=8)
            listbox.pack(pady=10, padx=20, fill="both", expand=True)
            
            for display_name, _, z_offset in available_diamonds:
                listbox.insert(tk.END, f"{display_name} (z: {z_offset:.1f})")
            
            # Pre-select current target if editing existing portal
            if current_elevation is not None:
                for i, (_, _, z_offset) in enumerate(available_diamonds):
                    if abs(z_offset - current_elevation) < 0.1:
                        listbox.selection_set(i)
                        break
            
            # Buttons
            button_frame = tk.Frame(root)
            button_frame.pack(pady=10)
            
            tk.Button(button_frame, text="Create Portal", command=on_select, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="Cancel", command=on_cancel, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
            
            # Double-click to select
            listbox.bind("<Double-Button-1>", lambda e: on_select())
            
            root.mainloop()
            
            return selected_z_offset
                
        except Exception as e:
            print(f"Error showing z-portal dialog: {e}")
            return None
    
    def _create_bidirectional_portal(self, source_edge_info, target_elevation):
        """Create a bi-directional z-portal on the target diamond"""
        current_sprite = self.ui.model.get_current_sprite()
        if not current_sprite or not current_sprite.diamond_info:
            return
        
        # Get current diamond's z-offset to calculate which diamond to target
        current_layer = self.ui.renderer.selected_sub_diamond_layer
        source_diamond_data = None
        
        if current_layer == 'lower' and current_sprite.diamond_info.lower_diamond:
            source_diamond_data = current_sprite.diamond_info.lower_diamond
        elif current_layer == 'upper' and current_sprite.diamond_info.upper_diamond:
            source_diamond_data = current_sprite.diamond_info.upper_diamond
        elif current_layer in current_sprite.diamond_info.extra_diamonds:
            source_diamond_data = current_sprite.diamond_info.extra_diamonds[current_layer]
        
        if not source_diamond_data:
            return
        
        # Calculate source z_offset using same logic as dialog and export (lower_north_y - source_north_y)
        lower_north_y = current_sprite.diamond_info.lower_diamond.north_vertex.y if current_sprite.diamond_info.lower_diamond else 0
        source_z_offset = float(lower_north_y - source_diamond_data.north_vertex.y)
        
        # Find target diamond that matches the target elevation
        target_diamond_data = None
        target_layer_name = None
        
        # Check lower diamond (always has calculated z_offset = 0.0)
        if current_sprite.diamond_info.lower_diamond:
            calculated_z_offset = 0.0
            if abs(calculated_z_offset - target_elevation) < 0.1:
                target_diamond_data = current_sprite.diamond_info.lower_diamond
                target_layer_name = 'lower'
        
        # Check upper diamond (z_offset = lower_north_y - upper_north_y)
        if not target_diamond_data and current_sprite.diamond_info.upper_diamond:
            calculated_z_offset = float(lower_north_y - current_sprite.diamond_info.upper_diamond.north_vertex.y)
            if abs(calculated_z_offset - target_elevation) < 0.1:
                target_diamond_data = current_sprite.diamond_info.upper_diamond
                target_layer_name = 'upper'
        
        # Check custom diamonds (z_offset = lower_north_y - custom_north_y)
        if not target_diamond_data:
            for layer_name, diamond_data in current_sprite.diamond_info.extra_diamonds.items():
                calculated_z_offset = float(lower_north_y - diamond_data.north_vertex.y)
                if abs(calculated_z_offset - target_elevation) < 0.1:
                    target_diamond_data = diamond_data
                    target_layer_name = layer_name
                    break
        
        if target_diamond_data and target_layer_name:
            # Ensure target diamond has sub-diamonds initialized
            target_diamond_data.ensure_sub_diamonds_initialized()
            
            if target_diamond_data.sub_diamonds:
                # Find corresponding edge on target diamond
                source_direction = source_edge_info['direction']
                source_edge_name = source_edge_info['edge_name']
                
                if source_direction in target_diamond_data.sub_diamonds:
                    target_sub_diamond = target_diamond_data.sub_diamonds[source_direction]
                    target_edge = getattr(target_sub_diamond, source_edge_name, None)
                    
                    if target_edge:
                        # Create return portal with source elevation
                        target_edge.z_portal = source_z_offset
                        print(f"Created bi-directional portal: {target_layer_name} {source_direction} {source_edge_name} -> elevation {source_z_offset}")
                    else:
                        print(f"Could not find target edge for bi-directional portal")
                else:
                    print(f"Target sub-diamond {source_direction} not found on {target_layer_name} layer")
            else:
                print(f"Target diamond {target_layer_name} has no sub-diamonds")
        else:
            print(f"Could not find target diamond at elevation {target_elevation} for bi-directional portal")
    
    def _remove_bidirectional_portal(self, source_edge_info, old_target_elevation):
        """Remove bi-directional z-portal from the target diamond"""
        current_sprite = self.ui.model.get_current_sprite()
        if not current_sprite or not current_sprite.diamond_info:
            return
        
        # Get the lower diamond's north vertex Y coordinate for z_offset calculation
        lower_north_y = current_sprite.diamond_info.lower_diamond.north_vertex.y if current_sprite.diamond_info.lower_diamond else 0
        
        # Find target diamond that was at the old target elevation
        target_diamond_data = None
        target_layer_name = None
        
        # Check lower diamond (always has calculated z_offset = 0.0)
        if current_sprite.diamond_info.lower_diamond:
            calculated_z_offset = 0.0
            if abs(calculated_z_offset - old_target_elevation) < 0.1:
                target_diamond_data = current_sprite.diamond_info.lower_diamond
                target_layer_name = 'lower'
        
        # Check upper diamond (z_offset = lower_north_y - upper_north_y)
        if not target_diamond_data and current_sprite.diamond_info.upper_diamond:
            calculated_z_offset = float(lower_north_y - current_sprite.diamond_info.upper_diamond.north_vertex.y)
            if abs(calculated_z_offset - old_target_elevation) < 0.1:
                target_diamond_data = current_sprite.diamond_info.upper_diamond
                target_layer_name = 'upper'
        
        # Check custom diamonds (z_offset = lower_north_y - custom_north_y)
        if not target_diamond_data:
            for layer_name, diamond_data in current_sprite.diamond_info.extra_diamonds.items():
                calculated_z_offset = float(lower_north_y - diamond_data.north_vertex.y)
                if abs(calculated_z_offset - old_target_elevation) < 0.1:
                    target_diamond_data = diamond_data
                    target_layer_name = layer_name
                    break
        
        if target_diamond_data and target_diamond_data.sub_diamonds:
            # Find corresponding edge on target diamond
            source_direction = source_edge_info['direction']
            source_edge_name = source_edge_info['edge_name']
            
            if source_direction in target_diamond_data.sub_diamonds:
                target_sub_diamond = target_diamond_data.sub_diamonds[source_direction]
                target_edge = getattr(target_sub_diamond, source_edge_name, None)
                
                if target_edge and target_edge.z_portal is not None:
                    target_edge.z_portal = None
                    print(f"Removed bi-directional portal from {target_layer_name} {source_direction} {source_edge_name}")
                else:
                    print(f"No bi-directional portal found on {target_layer_name} {source_direction} {source_edge_name}")
            else:
                print(f"Target sub-diamond {source_direction} not found on {target_layer_name} layer")
        else:
            print(f"Could not find target diamond at elevation {old_target_elevation} for bi-directional portal removal")
    
    def handle_propagate_rotation(self):
        """Propagate sub-diamond properties across all frames with automatic rotation mapping for ALL layers"""
        if not self.ui.model:
            print("Please load a spritesheet first before propagating rotations")
            return
        
        if not self.ui.renderer.sub_diamond_mode:
            print("Sub-diamond mode must be active to propagate rotations")
            return
        
        current_sprite_index = self.ui.model.current_sprite_index
        current_sprite = self.ui.model.get_current_sprite()
        
        if not current_sprite or not current_sprite.diamond_info:
            print("Current sprite has no diamond data to propagate")
            return
        
        # Collect ALL layers with sub-diamond data from source frame
        source_layers = []
        
        # Check lower diamond
        if current_sprite.diamond_info.lower_diamond and hasattr(current_sprite.diamond_info.lower_diamond, 'sub_diamonds'):
            current_sprite.diamond_info.lower_diamond.ensure_sub_diamonds_initialized()
            if current_sprite.diamond_info.lower_diamond.sub_diamonds:
                source_layers.append(('lower', current_sprite.diamond_info.lower_diamond))
        
        # Check upper diamond
        if current_sprite.diamond_info.upper_diamond and hasattr(current_sprite.diamond_info.upper_diamond, 'sub_diamonds'):
            current_sprite.diamond_info.upper_diamond.ensure_sub_diamonds_initialized()
            if current_sprite.diamond_info.upper_diamond.sub_diamonds:
                source_layers.append(('upper', current_sprite.diamond_info.upper_diamond))
        
        # Check custom diamonds
        if current_sprite.diamond_info.extra_diamonds:
            for custom_name, custom_diamond in current_sprite.diamond_info.extra_diamonds.items():
                if hasattr(custom_diamond, 'sub_diamonds'):
                    custom_diamond.ensure_sub_diamonds_initialized()
                    if custom_diamond.sub_diamonds:
                        source_layers.append((custom_name, custom_diamond))
        
        if not source_layers:
            print("No layers with sub-diamond data available for propagation")
            return
        
        print(f"\n=== PROPAGATING ALL LAYERS TO ALL FRAMES ===")
        print(f"Source frame: {current_sprite_index}")
        print(f"Total frames: {len(self.ui.model.sprites)}")
        print(f"Layers to propagate: {[layer_name for layer_name, _ in source_layers]}")
        
        # Track successful propagations
        total_propagations = 0
        successful_propagations = 0
        
        # First, ensure all target frames are analyzed
        print(f"Ensuring all frames are analyzed...")
        for target_frame_index in range(len(self.ui.model.sprites)):
            if target_frame_index == current_sprite_index:
                continue  # Skip source frame
            
            target_sprite = self.ui.model.sprites[target_frame_index]
            if not target_sprite:
                continue
            
            # Analyze target frame if not already analyzed
            if not target_sprite.diamond_info:
                print(f"  Analyzing frame {target_frame_index}...")
                self.ui.analyzer.analyze_sprite(target_frame_index)
                
                if not target_sprite.diamond_info:
                    print(f"  Warning: Failed to analyze frame {target_frame_index}")
                    continue
        
        # Now propagate all layers to all other frames
        for target_frame_index in range(len(self.ui.model.sprites)):
            if target_frame_index == current_sprite_index:
                continue  # Skip source frame
            
            target_sprite = self.ui.model.sprites[target_frame_index]
            if not target_sprite:
                continue
            
            # Calculate rotation steps (45° counter-clockwise per frame)
            rotation_steps = (target_frame_index - current_sprite_index) % len(self.ui.model.sprites)
            
            print(f"\nPropagating to frame {target_frame_index} (rotation steps: {rotation_steps})")
            
            # Propagate each layer
            frame_success_count = 0
            for layer_name, source_diamond_data in source_layers:
                total_propagations += 1
                
                # Create or get target diamond data
                if self._create_custom_diamond_for_frame(target_sprite, layer_name, source_diamond_data):
                    # Apply rotation mapping to properties
                    if self._apply_rotation_mapping(target_sprite, layer_name, source_diamond_data, rotation_steps):
                        successful_propagations += 1
                        frame_success_count += 1
                        print(f"  ✓ {layer_name} layer propagated")
                    else:
                        print(f"  ✗ Failed to apply rotation mapping to {layer_name} layer")
                else:
                    print(f"  ✗ Failed to create {layer_name} layer")
            
            print(f"Frame {target_frame_index}: {frame_success_count}/{len(source_layers)} layers successful")
        
        # Clear cache and update display
        self.ui.renderer._clear_sprite_display_cache()
        self.ui.update_sprite_info()
        
        print(f"\n=== PROPAGATION COMPLETE ===")
        print(f"Successfully propagated {successful_propagations}/{total_propagations} layer instances")
        print(f"Across {len(self.ui.model.sprites)-1} target frames")
        print(f"Rotation pattern: N→W→S→E (45° counter-clockwise per frame)")
    
    def _create_custom_diamond_for_frame(self, target_sprite, source_layer, source_diamond_data):
        """Create or ensure diamond layer exists for target frame at same z-height"""
        from spritesheet_model import GameplayDiamondData
        
        # Check if target sprite has diamond_info
        if not target_sprite.diamond_info:
            print(f"  Warning: Target frame has no diamond analysis data - skipping")
            return False
        
        # Handle lower diamond - should always exist from analysis
        if source_layer == 'lower':
            if not target_sprite.diamond_info.lower_diamond:
                print(f"  Warning: Target frame missing lower diamond - this should exist from analysis")
                return False
            print(f"  Lower diamond already exists")
            return True
        
        # Handle upper diamond
        elif source_layer == 'upper':
            if not target_sprite.diamond_info.upper_diamond:
                if not target_sprite.diamond_info.lower_diamond:
                    print(f"  Cannot create upper diamond - no lower diamond available")
                    return False
                
                print(f"  Creating upper diamond at same z-height")
                # Create upper diamond based on lower diamond with same z_offset as source
                lower_diamond = target_sprite.diamond_info.lower_diamond
                target_sprite.diamond_info.upper_diamond = GameplayDiamondData(
                    north_vertex=lower_diamond.north_vertex,
                    south_vertex=lower_diamond.south_vertex,
                    east_vertex=lower_diamond.east_vertex,
                    west_vertex=lower_diamond.west_vertex,
                    center=lower_diamond.center,
                    z_offset=source_diamond_data.z_offset,
                    north_east_midpoint=lower_diamond.north_east_midpoint,
                    east_south_midpoint=lower_diamond.east_south_midpoint,
                    south_west_midpoint=lower_diamond.south_west_midpoint,
                    west_north_midpoint=lower_diamond.west_north_midpoint
                )
                # Ensure sub-diamonds are initialized
                target_sprite.diamond_info.upper_diamond.ensure_sub_diamonds_initialized()
            print(f"  Upper diamond ready")
            return True
        
        # Handle custom diamonds
        else:
            if source_layer not in target_sprite.diamond_info.extra_diamonds:
                if not target_sprite.diamond_info.lower_diamond:
                    print(f"  Cannot create custom diamond - no lower diamond available")
                    return False
                
                print(f"  Creating custom diamond '{source_layer}' at same z-height")
                # Create custom diamond with correct vertices based on source z_offset
                lower_diamond = target_sprite.diamond_info.lower_diamond
                
                # Calculate correct vertices by shifting lower diamond by z_offset difference
                z_offset_diff = int(source_diamond_data.z_offset)  # How much higher than lower diamond
                
                from spritesheet_model import Point
                target_sprite.diamond_info.extra_diamonds[source_layer] = GameplayDiamondData(
                    north_vertex=Point(x=lower_diamond.north_vertex.x, y=lower_diamond.north_vertex.y - z_offset_diff),
                    south_vertex=Point(x=lower_diamond.south_vertex.x, y=lower_diamond.south_vertex.y - z_offset_diff),
                    east_vertex=Point(x=lower_diamond.east_vertex.x, y=lower_diamond.east_vertex.y - z_offset_diff),
                    west_vertex=Point(x=lower_diamond.west_vertex.x, y=lower_diamond.west_vertex.y - z_offset_diff),
                    center=Point(x=lower_diamond.center.x, y=lower_diamond.center.y - z_offset_diff),
                    z_offset=source_diamond_data.z_offset,
                    north_east_midpoint=Point(x=lower_diamond.north_east_midpoint.x, y=lower_diamond.north_east_midpoint.y - z_offset_diff),
                    east_south_midpoint=Point(x=lower_diamond.east_south_midpoint.x, y=lower_diamond.east_south_midpoint.y - z_offset_diff),
                    south_west_midpoint=Point(x=lower_diamond.south_west_midpoint.x, y=lower_diamond.south_west_midpoint.y - z_offset_diff),
                    west_north_midpoint=Point(x=lower_diamond.west_north_midpoint.x, y=lower_diamond.west_north_midpoint.y - z_offset_diff)
                )
                # Ensure sub-diamonds are initialized for the new custom diamond
                target_sprite.diamond_info.extra_diamonds[source_layer].ensure_sub_diamonds_initialized()
                print(f"  Custom diamond '{source_layer}' created with z_offset {source_diamond_data.z_offset}")
            else:
                print(f"  Custom diamond '{source_layer}' already exists")
            print(f"  Custom diamond '{source_layer}' ready")
            return True
    
    def _apply_rotation_mapping(self, target_sprite, target_layer, source_diamond_data, rotation_steps):
        """Apply rotational transformation logic: N→W→S→E→N pattern"""
        # Get target diamond data
        target_diamond_data = None
        if target_layer == 'lower':
            target_diamond_data = target_sprite.diamond_info.lower_diamond
        elif target_layer == 'upper':
            target_diamond_data = target_sprite.diamond_info.upper_diamond
        elif target_layer in target_sprite.diamond_info.extra_diamonds:
            target_diamond_data = target_sprite.diamond_info.extra_diamonds[target_layer]
        
        if not target_diamond_data:
            print(f"    No target diamond data found for {target_layer}")
            return False
        
        # Ensure target diamond has sub-diamonds initialized
        target_diamond_data.ensure_sub_diamonds_initialized()
        
        if not target_diamond_data.sub_diamonds:
            print(f"    No sub-diamonds initialized for target {target_layer}")
            return False
        
        # Define rotation mapping: N→W→S→E→N (45° counter-clockwise)
        direction_rotation = {
            'north': ['north', 'west', 'south', 'east'],
            'west': ['west', 'south', 'east', 'north'],
            'south': ['south', 'east', 'north', 'west'],
            'east': ['east', 'north', 'west', 'south']
        }
        
        print(f"    Applying {rotation_steps} rotation steps (N→W→S→E pattern)")
        
        # Copy properties with rotation mapping
        for source_direction, source_sub_diamond in source_diamond_data.sub_diamonds.items():
            if source_direction not in direction_rotation:
                print(f"    Warning: Unknown source direction {source_direction}")
                continue
            
            # Calculate target direction after rotation
            rotation_sequence = direction_rotation[source_direction]
            target_direction = rotation_sequence[rotation_steps % 4]
            
            if target_direction not in target_diamond_data.sub_diamonds:
                print(f"    Warning: Target direction {target_direction} not found in target diamond")
                continue
            
            target_sub_diamond = target_diamond_data.sub_diamonds[target_direction]
            
            print(f"    {source_direction} → {target_direction}")
            
            # Copy surface properties
            target_sub_diamond.is_walkable = source_sub_diamond.is_walkable
            
            # Copy edge properties with rotation
            self._copy_edge_properties_with_rotation(source_sub_diamond, target_sub_diamond, rotation_steps)
        
        # Update shared edges to maintain consistency
        self._update_all_shared_edges(target_diamond_data.sub_diamonds)
        
        print(f"    Rotation mapping applied successfully")
        return True
    
    def _copy_edge_properties_with_rotation(self, source_sub_diamond, target_sub_diamond, rotation_steps):
        """Copy edge properties with proper edge rotation mapping"""
        # Define edge rotation mapping: edges rotate with the sub-diamond
        # Each edge rotates 45° counter-clockwise with each step
        edge_rotation = {
            'north_west_edge': ['north_west_edge', 'south_west_edge', 'south_east_edge', 'north_east_edge'],
            'north_east_edge': ['north_east_edge', 'north_west_edge', 'south_west_edge', 'south_east_edge'],
            'south_west_edge': ['south_west_edge', 'south_east_edge', 'north_east_edge', 'north_west_edge'],
            'south_east_edge': ['south_east_edge', 'north_east_edge', 'north_west_edge', 'south_west_edge']
        }
        
        # Copy each edge with rotation
        for source_edge_name in ['north_west_edge', 'north_east_edge', 'south_west_edge', 'south_east_edge']:
            source_edge = getattr(source_sub_diamond, source_edge_name, None)
            if not source_edge:
                continue
            
            # Calculate target edge after rotation
            if source_edge_name not in edge_rotation:
                continue
            
            rotation_sequence = edge_rotation[source_edge_name]
            target_edge_name = rotation_sequence[rotation_steps % 4]
            
            target_edge = getattr(target_sub_diamond, target_edge_name, None)
            if not target_edge:
                continue
            
            # Copy properties
            target_edge.blocks_line_of_sight = source_edge.blocks_line_of_sight
            target_edge.blocks_movement = source_edge.blocks_movement
            target_edge.z_portal = source_edge.z_portal
            
            print(f"      {source_edge_name} → {target_edge_name}")