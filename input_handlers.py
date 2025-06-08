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
        elif event.ui_element == ui_elements['analysis_auto_populate_button']:
            self.handle_auto_populate_vertices()
        elif event.ui_element == ui_elements['analysis_delete_keypoints_button']:
            self.handle_delete_all_custom_keypoints()
        elif event.ui_element == ui_elements['analysis_reset_vertices_button']:
            self.handle_reset_manual_vertices()
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
    
    def _update_vertex_info_label(self):
        """Update the vertex selection info label"""
        if hasattr(self.ui.analysis_controls_panel.components, 'vertex_info_label'):
            vertex_name = self.ui.renderer._get_vertex_name(self.ui.renderer.selected_vertex)
            diamond_name = self.ui.renderer.selected_diamond.title()
            info_text = f'Selected: {diamond_name} {vertex_name} ({self.ui.renderer.selected_vertex})\n'
            info_text += 'Keys: 1234=NSEW F1/F2=Lower/Upper\n'
            info_text += 'Left-click add, Right-click remove'
            self.ui.analysis_controls_panel.components['vertex_info_label'].set_text(info_text)
    
    def handle_auto_populate_vertices(self):
        """Auto-populate missing vertices based on manual inputs and geometric relationships"""
        if not self.ui.model or not self.ui.renderer.manual_vertex_mode:
            print("Auto-populate requires manual vertex mode to be enabled")
            return
        
        sprite_key = self.ui.model.current_sprite_index
        current_sprite = self.ui.model.get_current_sprite()
        if not current_sprite or not current_sprite.bbox:
            print("No sprite data available for auto-populate")
            return
        
        manual_data = self.ui.renderer.manual_vertices.get(sprite_key, {})
        if not manual_data:
            print("No manual vertices to work with")
            return
        
        bbox = current_sprite.bbox
        # Use effective diamond width instead of bbox width for proper calculation
        effective_diamond_width = self.ui.model.get_effective_diamond_width(sprite_key)
        
        print(f"\n=== AUTO-POPULATE VERTICES ===")
        print(f"Starting with: {manual_data}")
        print(f"Using effective diamond width: {effective_diamond_width} (bbox width: {bbox.width})")
        
        # Initialize if needed
        if sprite_key not in self.ui.renderer.manual_vertices:
            self.ui.renderer.manual_vertices[sprite_key] = {}
        
        # Step 1: Complete each diamond that has >= 2 points
        for diamond_level in ['lower', 'upper']:
            diamond_data = manual_data.get(diamond_level, {})
            point_count = len(diamond_data)
            
            if point_count >= 2:
                print(f"Completing {diamond_level} diamond ({point_count} points)")
                completed_diamond = self._complete_diamond_from_points(diamond_data, effective_diamond_width)
                
                # Update manual vertices with completed diamond
                if diamond_level not in self.ui.renderer.manual_vertices[sprite_key]:
                    self.ui.renderer.manual_vertices[sprite_key][diamond_level] = {}
                self.ui.renderer.manual_vertices[sprite_key][diamond_level].update(completed_diamond)
        
        # Step 2: Handle cross-diamond derivation if needed
        lower_data = self.ui.renderer.manual_vertices[sprite_key].get('lower', {})
        upper_data = self.ui.renderer.manual_vertices[sprite_key].get('upper', {})
        
        lower_complete = len(lower_data) >= 4
        upper_complete = len(upper_data) >= 4
        
        if lower_complete and not upper_complete and len(upper_data) >= 1:
            # Derive z_lower from one upper point and complete upper diamond
            z_lower = self._derive_z_lower_from_diamonds(lower_data, upper_data)
            print(f"Derived z_lower: {z_lower}")
            completed_upper = self._derive_diamond_from_other(lower_data, -z_lower)  # Upper is ABOVE lower (smaller Y)
            
            if 'upper' not in self.ui.renderer.manual_vertices[sprite_key]:
                self.ui.renderer.manual_vertices[sprite_key]['upper'] = {}
            self.ui.renderer.manual_vertices[sprite_key]['upper'].update(completed_upper)
            
        elif upper_complete and not lower_complete and len(lower_data) >= 1:
            # Derive z_lower from one lower point and complete lower diamond
            z_lower = self._derive_z_lower_from_diamonds(upper_data, lower_data)
            print(f"Derived z_lower: {z_lower}")
            completed_lower = self._derive_diamond_from_other(upper_data, z_lower)  # Lower is BELOW upper (larger Y)
            
            if 'lower' not in self.ui.renderer.manual_vertices[sprite_key]:
                self.ui.renderer.manual_vertices[sprite_key]['lower'] = {}
            self.ui.renderer.manual_vertices[sprite_key]['lower'].update(completed_lower)
            
        elif lower_complete and not upper_complete:
            # Use algorithmic z_lower to create upper diamond
            if current_sprite.diamond_info:
                z_lower = current_sprite.diamond_info.lower_z_offset
                print(f"Using algorithmic z_lower: {z_lower}")
                completed_upper = self._derive_diamond_from_other(lower_data, -z_lower)  # Upper is ABOVE lower
                
                if 'upper' not in self.ui.renderer.manual_vertices[sprite_key]:
                    self.ui.renderer.manual_vertices[sprite_key]['upper'] = {}
                self.ui.renderer.manual_vertices[sprite_key]['upper'].update(completed_upper)
                
        elif upper_complete and not lower_complete:
            # Use algorithmic z_lower to create lower diamond
            if current_sprite.diamond_info:
                z_lower = current_sprite.diamond_info.lower_z_offset
                print(f"Using algorithmic z_lower: {z_lower}")
                completed_lower = self._derive_diamond_from_other(upper_data, z_lower)  # Lower is BELOW upper
                
                if 'lower' not in self.ui.renderer.manual_vertices[sprite_key]:
                    self.ui.renderer.manual_vertices[sprite_key]['lower'] = {}
                self.ui.renderer.manual_vertices[sprite_key]['lower'].update(completed_lower)
        
        print(f"Final result: {self.ui.renderer.manual_vertices[sprite_key]}")
        
        # Clear cache and update display
        self.ui.renderer._clear_sprite_display_cache()
        self.ui.update_sprite_info()
    
    def _complete_diamond_from_points(self, diamond_data, diamond_width):
        """Complete a diamond using geometric relationships from existing points"""
        completed = {}
        
        # Copy existing points
        for vertex, coords in diamond_data.items():
            completed[vertex] = coords
        
        # Apply geometric relationships to fill missing points
        # NOTE: In screen coords, Y increases downward, so "up" = smaller Y
        if 'south' in diamond_data and 'north' not in completed:
            # North is directly above South by diamond_width//2 (smaller Y)
            sx, sy = diamond_data['south']
            completed['north'] = (sx, sy - diamond_width // 2)
            
        if 'north' in diamond_data and 'south' not in completed:
            # South is directly below North by diamond_width//2 (larger Y)
            nx, ny = diamond_data['north']
            completed['south'] = (nx, ny + diamond_width // 2)
            
        if 'west' in diamond_data and 'east' not in completed:
            # East is directly right of West by diamond_width
            wx, wy = diamond_data['west']
            completed['east'] = (wx + diamond_width, wy)
            
        if 'east' in diamond_data and 'west' not in completed:
            # West is directly left of East by diamond_width
            ex, ey = diamond_data['east']
            completed['west'] = (ex - diamond_width, ey)
        
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
    
    def handle_pixeloid_up(self):
        """Handle pixeloid increase"""
        if self.ui.model:
            self.ui.model.pixeloid_multiplier = min(32, self.ui.model.pixeloid_multiplier * 2)
            self.ui.view_controls_panel.components['pixeloid_label'].set_text(f'Pixeloid: {self.ui.model.pixeloid_multiplier}x')
            # Clear cache since pixeloid affects rendering
            self.ui.renderer._clear_sprite_display_cache()
    
    def handle_pixeloid_down(self):
        """Handle pixeloid decrease"""
        if self.ui.model:
            self.ui.model.pixeloid_multiplier = max(1, self.ui.model.pixeloid_multiplier // 2)
            self.ui.view_controls_panel.components['pixeloid_label'].set_text(f'Pixeloid: {self.ui.model.pixeloid_multiplier}x')
            # Clear cache since pixeloid affects rendering
            self.ui.renderer._clear_sprite_display_cache()
    
    def handle_reset_view(self):
        """Handle view reset"""
        if self.ui.model:
            self.ui.model.pixeloid_multiplier = 1
            self.ui.model.pan_x = 0
            self.ui.model.pan_y = 0
            self.ui.view_controls_panel.components['pixeloid_label'].set_text(f'Pixeloid: {self.ui.model.pixeloid_multiplier}x')
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
                self.ui.view_controls_panel.components['pixeloid_label'].set_text(f'Pixeloid: {self.ui.model.pixeloid_multiplier}x')
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
        """Handle left-click for adding manual vertices or custom keypoints"""
        if not self.ui.model:
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
        """Handle right-click for removing manual vertices or custom keypoints"""
        if not self.ui.model:
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
        
        for diamond_level in ['lower', 'upper']:
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
        # F3 key toggles custom keypoints mode (works regardless of other modes)
        if key == pygame.K_F3:
            self.handle_toggle_custom_keypoints_mode()
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
        elif key == pygame.K_F2:
            self.ui.renderer.selected_diamond = 'upper'
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