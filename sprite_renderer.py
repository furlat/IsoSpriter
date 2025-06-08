import pygame
import pygame_gui
from typing import Optional, Tuple, Set
from spritesheet_model import SpritesheetModel, SpriteData


class SpriteRenderer:
    """Handles all sprite rendering and fancy calculations - extracted from AdvancedSpritesheetUI"""
    
    def __init__(self, drawing_area_width: int, drawing_area_height: int, left_panel_width: int):
        self.DRAWING_AREA_WIDTH = drawing_area_width
        self.DRAWING_AREA_HEIGHT = drawing_area_height
        self.LEFT_PANEL_WIDTH = left_panel_width
        
        # Rendering cache for draw_sprite_display computations
        self._sprite_display_cache = {}
        self._cache_size_limit = 50  # Limit cache size to prevent memory issues
        
        # Initialize fonts for rendering
        pygame.font.init()
        self._font = pygame.font.Font(None, 24)  # Default font, size 24
        self._vertex_font = None  # Will be initialized when needed
        
        # Diamond visualization modes (these will be set by the main UI)
        self.show_diamond_lines = False  # Show blue diamond outline
        self.show_raycast_analysis = True  # Show raycast lines and points
        
        # Manual vertex editing state (these will be set by the main UI)
        self.manual_vertex_mode = False
        self.selected_vertex = 1  # 1=N, 2=S, 3=E, 4=W
        self.selected_diamond = 'lower'  # 'lower' or 'upper'
        self.manual_vertices = {}  # Dictionary to store manual vertex overrides per sprite
        
        # Custom keypoints mode (F3 mode)
        self.custom_keypoints_mode = False
        self.custom_keypoints = {}  # Dictionary to store custom keypoints per sprite: {sprite_index: {'keypoint_name': (x, y)}}
    
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
                       show_diamond_vertices: bool, effective_upper_z: int, pan_x: int, pan_y: int, model: Optional[SpritesheetModel] = None) -> tuple:
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
        
        # Include custom keypoints in cache key
        custom_keypoints_key = None
        if self.custom_keypoints_mode and sprite_index in self.custom_keypoints:
            custom_data = self.custom_keypoints[sprite_index]
            if custom_data:
                custom_keypoints_key = tuple(sorted(custom_data.items()))
        
        # Include manual diamond width in cache key since it affects rendering
        manual_diamond_width_key = None
        if model:
            current_sprite = model.get_current_sprite()
            if current_sprite and current_sprite.manual_diamond_width is not None:
                manual_diamond_width_key = current_sprite.manual_diamond_width
            elif model.manual_diamond_width is not None:
                manual_diamond_width_key = ('global', model.manual_diamond_width)
        
        return (sprite_index, pixeloid_mult, alpha_threshold, show_overlay,
                show_diamond, upper_lines_mode, show_diamond_vertices, effective_upper_z,
                pan_x, pan_y, self.manual_vertex_mode, manual_vertices_key,
                self.show_diamond_lines, self.show_raycast_analysis,
                self.custom_keypoints_mode, custom_keypoints_key, manual_diamond_width_key)
    
    def _limit_cache_size(self):
        """Remove oldest cache entries if cache size exceeds limit"""
        if len(self._sprite_display_cache) > self._cache_size_limit:
            # Remove oldest entries (simple FIFO approach)
            keys_to_remove = list(self._sprite_display_cache.keys())[:-self._cache_size_limit]
            for key in keys_to_remove:
                del self._sprite_display_cache[key]
    
    def _calculate_expanded_bounds(self, current_sprite, model):
        """Calculate expanded bounds to fit manual diamond width visualization and manual vertex positions"""
        if not current_sprite.bbox or not current_sprite.diamond_info:
            return None
        
        bbox = current_sprite.bbox
        effective_diamond_width = model.get_effective_diamond_width(model.current_sprite_index)
        
        # Calculate diamond bounds
        diamond_center_x = bbox.x + bbox.width // 2
        diamond_left = diamond_center_x - effective_diamond_width // 2
        diamond_right = diamond_center_x + effective_diamond_width // 2
        
        # Start with diamond and bbox bounds
        expanded_left = min(bbox.x, diamond_left)
        expanded_right = max(bbox.x + bbox.width, diamond_right)
        expanded_top = bbox.y
        expanded_bottom = bbox.y + bbox.height
        
        # Check manual vertex positions to extend bounds further if needed
        sprite_key = model.current_sprite_index
        manual_overrides = self.manual_vertices.get(sprite_key, {})
        
        for diamond_level in ['lower', 'upper']:
            level_vertices = manual_overrides.get(diamond_level, {})
            for vertex_name, (abs_x, abs_y) in level_vertices.items():
                # Expand bounds to include manual vertex positions
                expanded_left = min(expanded_left, abs_x)
                expanded_right = max(expanded_right, abs_x)
                expanded_top = min(expanded_top, abs_y)
                expanded_bottom = max(expanded_bottom, abs_y)
        
        # Calculate final expanded dimensions
        expanded_width = expanded_right - expanded_left
        expanded_height = expanded_bottom - expanded_top
        
        expanded_bounds = {
            'x': expanded_left,
            'y': expanded_top,
            'width': expanded_width,
            'height': expanded_height,
            'original_bbox': bbox,
            'diamond_extends': expanded_width > bbox.width or expanded_height > bbox.height
        }
        
        return expanded_bounds
    
    def draw_sprite_display(self, screen: pygame.Surface, model: Optional[SpritesheetModel], analyzer, left_panel_width: int):
        """Draw the current sprite with pixeloid rendering in the center area (cached)"""
        if not model or not analyzer:
            return
        
        current_sprite = model.get_current_sprite()
        if not current_sprite:
            return
            
        sprite_surface = analyzer.get_sprite_surface(model.current_sprite_index)
        if not sprite_surface:
            return
        
        sprite_rect = sprite_surface.get_rect()
        if sprite_rect.width <= 0 or sprite_rect.height <= 0:
            return
        
        # Calculate expanded bounds for manual diamond width visualization
        expanded_bounds = self._calculate_expanded_bounds(current_sprite, model)
        
        # Generate cache key for current rendering parameters
        effective_upper_z = model.get_effective_upper_z_offset(model.current_sprite_index)
        cache_key = self._get_cache_key(
            model.current_sprite_index,
            model.pixeloid_multiplier,
            model.alpha_threshold,
            model.show_overlay,
            model.show_diamond_height,
            model.upper_lines_midpoint_mode,
            model.show_diamond_vertices,
            effective_upper_z,
            model.pan_x,
            model.pan_y,
            model
        )
        
        # Check if we have a cached surface for these parameters
        if cache_key in self._sprite_display_cache:
            cached_surface, cached_clip_rect = self._sprite_display_cache[cache_key]
            # Blit the cached surface to the screen
            screen.set_clip(cached_clip_rect)
            screen.blit(cached_surface, (left_panel_width, 0))
            screen.set_clip(None)
        else:
            # Determine rendering dimensions based on expanded bounds
            render_width = self.DRAWING_AREA_WIDTH
            render_height = self.DRAWING_AREA_HEIGHT
            
            # If diamond extends beyond bbox, we might need larger rendering area
            if expanded_bounds and expanded_bounds['diamond_extends']:
                # For now, keep the same drawing area but adjust sprite positioning
                pass
            
            # Create a new surface to render to for caching
            cache_surface = pygame.Surface((render_width, render_height))
            cache_surface.fill((40, 40, 40))  # Match background color
            
            # Render to the cache surface with expanded bounds information
            self._render_sprite_to_surface(cache_surface, sprite_surface, sprite_rect, current_sprite, model, expanded_bounds)
            
            # Calculate clipping rectangle
            drawing_x = left_panel_width
            drawing_y = 0
            clip_rect = pygame.Rect(drawing_x, drawing_y, self.DRAWING_AREA_WIDTH, self.DRAWING_AREA_HEIGHT)
            
            # Store in cache
            self._sprite_display_cache[cache_key] = (cache_surface.copy(), clip_rect)
            self._limit_cache_size()
            
            # Blit to screen
            screen.set_clip(clip_rect)
            screen.blit(cache_surface, (left_panel_width, 0))
            screen.set_clip(None)
        
        # Draw border around drawing area (not cached as it's always the same)
        pygame.draw.rect(screen, (100, 100, 100),
                        (left_panel_width - 1, -1, self.DRAWING_AREA_WIDTH + 2, self.DRAWING_AREA_HEIGHT + 2), 1)
    
    def draw_mouse_position_display(self, screen: pygame.Surface, model: Optional[SpritesheetModel],
                                   mouse_in_drawing_area: bool, sprite_pixel_x: float, sprite_pixel_y: float,
                                   window_width: int):
        """Draw the mouse position in pixeloid coordinates at the top center of screen"""
        if not model or not mouse_in_drawing_area:
            return
        
        # Format the pixeloid position text
        pixel_x_int = int(sprite_pixel_x)
        pixel_y_int = int(sprite_pixel_y)
        position_text = f"Pixeloid Position: ({pixel_x_int}, {pixel_y_int})"
        
        # Render the text
        text_surface = self._font.render(position_text, True, (255, 255, 255))  # White text
        text_rect = text_surface.get_rect()
        
        # Position at top center of screen
        text_x = (window_width - text_rect.width) // 2
        text_y = 10  # 10 pixels from top
        
        # Draw background rectangle for better visibility
        background_rect = pygame.Rect(text_x - 5, text_y - 2, text_rect.width + 10, text_rect.height + 4)
        pygame.draw.rect(screen, (0, 0, 0, 180), background_rect)  # Semi-transparent black background
        pygame.draw.rect(screen, (100, 100, 100), background_rect, 1)  # Gray border
        
        # Draw the text
        screen.blit(text_surface, (text_x, text_y))
    
    def _render_sprite_to_surface(self, surface: pygame.Surface, sprite_surface: pygame.Surface,
                                 sprite_rect: pygame.Rect, current_sprite, model: Optional[SpritesheetModel], expanded_bounds=None):
        """Render sprite content to the given surface (used for caching)"""
        if not model:
            return
        
        # Calculate sprite display size using pixeloid multiplier
        display_width = sprite_rect.width * model.pixeloid_multiplier
        display_height = sprite_rect.height * model.pixeloid_multiplier
        
        # Adjust sprite positioning if using expanded bounds for diamond visualization
        if expanded_bounds and expanded_bounds['diamond_extends']:
            # Calculate expanded display dimensions
            expanded_display_width = expanded_bounds['width'] * model.pixeloid_multiplier
            expanded_display_height = expanded_bounds['height'] * model.pixeloid_multiplier
            
            # Center the expanded area, then offset for original sprite position
            base_expanded_x = (self.DRAWING_AREA_WIDTH - expanded_display_width) // 2
            base_expanded_y = (self.DRAWING_AREA_HEIGHT - expanded_display_height) // 2
            
            # Calculate sprite offset within expanded area
            bbox_offset_x = (expanded_bounds['original_bbox'].x - expanded_bounds['x']) * model.pixeloid_multiplier
            bbox_offset_y = (expanded_bounds['original_bbox'].y - expanded_bounds['y']) * model.pixeloid_multiplier
            
            sprite_x = base_expanded_x + bbox_offset_x + model.pan_x
            sprite_y = base_expanded_y + bbox_offset_y + model.pan_y
        else:
            # Center the sprite in the surface, apply panning (original logic)
            base_sprite_x = (self.DRAWING_AREA_WIDTH - display_width) // 2
            base_sprite_y = (self.DRAWING_AREA_HEIGHT - display_height) // 2
            sprite_x = base_sprite_x + model.pan_x
            sprite_y = base_sprite_y + model.pan_y
        
        # Calculate padding in pixeloids
        padding_pixeloids = 10 * model.pixeloid_multiplier
        actual_display_width = display_width + (padding_pixeloids * 2)
        actual_display_height = display_height + (padding_pixeloids * 2)
        
        # Calculate the top-left of the padded area
        padded_x = sprite_x - padding_pixeloids
        padded_y = sprite_y - padding_pixeloids
        
        # Draw checkerboard background aligned with pixeloid boundaries
        pixeloid_size = model.pixeloid_multiplier
        
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
                
                if rect_w > 0 and rect_h > 0 and rect_x >= 0 and rect_y >= 0 and rect_x < self.DRAWING_AREA_WIDTH and rect_y < self.DRAWING_AREA_HEIGHT:
                    pygame.draw.rect(surface, color, (rect_x, rect_y, rect_w, rect_h))
                
                x += pixeloid_size
                col += 1
            y += pixeloid_size
            row += 1
        
        # Draw sprite pixel by pixel as pixeloids
        for y in range(sprite_rect.height):
            for x in range(sprite_rect.width):
                pixel_color = sprite_surface.get_at((x, y))
                if pixel_color.a > model.alpha_threshold:  # Only draw visible pixels
                    pixel_x = sprite_x + x * model.pixeloid_multiplier
                    pixel_y = sprite_y + y * model.pixeloid_multiplier
                    if (pixel_x >= 0 and pixel_y >= 0 and
                        pixel_x < self.DRAWING_AREA_WIDTH and pixel_y < self.DRAWING_AREA_HEIGHT):
                        pixel_rect = pygame.Rect(
                            pixel_x, pixel_y,
                            model.pixeloid_multiplier,
                            model.pixeloid_multiplier
                        )
                        pygame.draw.rect(surface, pixel_color[:3], pixel_rect)
        
        # Draw overlay if enabled
        if model.show_overlay:
            # Draw overlay pixel by pixel as pixeloids
            for y in range(sprite_rect.height):
                for x in range(sprite_rect.width):
                    pixel_color = sprite_surface.get_at((x, y))
                    if pixel_color.a > model.alpha_threshold:
                        # Create overlay color (green to red gradient)
                        alpha_val = pixel_color.a
                        intensity = (alpha_val - model.alpha_threshold) / (255 - model.alpha_threshold) if model.alpha_threshold < 255 else 1
                        overlay_color = (int(255 * intensity), int(255 * (1 - intensity)), 0)
                        
                        pixel_x = sprite_x + x * model.pixeloid_multiplier
                        pixel_y = sprite_y + y * model.pixeloid_multiplier
                        if (pixel_x >= 0 and pixel_y >= 0 and
                            pixel_x < self.DRAWING_AREA_WIDTH and pixel_y < self.DRAWING_AREA_HEIGHT):
                            overlay_rect = pygame.Rect(
                                pixel_x, pixel_y,
                                model.pixeloid_multiplier,
                                model.pixeloid_multiplier
                            )
                            # Draw semi-transparent overlay
                            overlay_surface = pygame.Surface((model.pixeloid_multiplier, model.pixeloid_multiplier))
                            overlay_surface.set_alpha(128)
                            overlay_surface.fill(overlay_color)
                            surface.blit(overlay_surface, overlay_rect)
            
            # Draw bounding box and analysis if sprite has analysis data
            if current_sprite.bbox:
                bbox = current_sprite.bbox
                
                # Scale bounding box coordinates using pixeloid multiplier
                scaled_bbox = pygame.Rect(
                    bbox.x * model.pixeloid_multiplier,
                    bbox.y * model.pixeloid_multiplier,
                    bbox.width * model.pixeloid_multiplier,
                    bbox.height * model.pixeloid_multiplier
                )
                
                # Draw original sprite boundary (blue lines)
                original_width_scaled = sprite_rect.width * model.pixeloid_multiplier
                original_height_scaled = sprite_rect.height * model.pixeloid_multiplier
                
                line_width = max(1, min(model.pixeloid_multiplier, 8))  # Cap line width to prevent issues
                
                # Draw solid blue rectangle for original boundaries - check if any part is visible
                original_rect = pygame.Rect(sprite_x, sprite_y, original_width_scaled, original_height_scaled)
                drawing_area_rect = pygame.Rect(0, 0, self.DRAWING_AREA_WIDTH, self.DRAWING_AREA_HEIGHT)
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
                if model.show_diamond_height and current_sprite.diamond_info:
                    diamond_info = current_sprite.diamond_info
                    
                    # Get effective upper Z offset for this frame
                    effective_upper_z = model.get_effective_upper_z_offset(model.current_sprite_index)
                    
                    # Draw upper Z offset line if present (cyan)
                    if effective_upper_z > 0:
                        upper_line_y_scaled = effective_upper_z * model.pixeloid_multiplier
                        upper_line_start_x = sprite_x + scaled_bbox.x
                        upper_line_end_x = sprite_x + scaled_bbox.x + scaled_bbox.width
                        upper_line_y_pos = sprite_y + scaled_bbox.y + upper_line_y_scaled
                        
                        # Draw horizontal line as cyan line - check if line is visible
                        if (upper_line_y_pos >= 0 and upper_line_y_pos < self.DRAWING_AREA_HEIGHT and
                            not (upper_line_end_x < 0 or upper_line_start_x >= self.DRAWING_AREA_WIDTH)):
                            # Clip line to visible area
                            clipped_start_x = max(0, upper_line_start_x)
                            clipped_end_x = min(self.DRAWING_AREA_WIDTH - 1, upper_line_end_x)
                            pygame.draw.line(surface, (0, 255, 255),
                                           (clipped_start_x, upper_line_y_pos), (clipped_end_x, upper_line_y_pos), line_width)
                    
                    # Draw the diamond height line (cyan)
                    if diamond_info.line_y and diamond_info.line_y >= bbox.y and diamond_info.line_y <= bbox.y + bbox.height:
                        # Scale the line position
                        line_y_scaled = (diamond_info.line_y - bbox.y) * model.pixeloid_multiplier
                        line_start_x = sprite_x + scaled_bbox.x
                        line_end_x = sprite_x + scaled_bbox.x + scaled_bbox.width
                        line_y_pos = sprite_y + scaled_bbox.y + line_y_scaled
                        
                        # Draw horizontal line as cyan line - check if line is visible
                        if (line_y_pos >= 0 and line_y_pos < self.DRAWING_AREA_HEIGHT and
                            not (line_end_x < 0 or line_start_x >= self.DRAWING_AREA_WIDTH)):
                            # Clip line to visible area
                            clipped_start_x = max(0, line_start_x)
                            clipped_end_x = min(self.DRAWING_AREA_WIDTH - 1, line_end_x)
                            pygame.draw.line(surface, (0, 255, 255),
                                           (clipped_start_x, line_y_pos), (clipped_end_x, line_y_pos), line_width)
                
                # Draw analysis points if available
                # Draw diamond lines if enabled (BEHIND analysis points)
                if self.show_diamond_lines and current_sprite.diamond_info:
                    pixeloid_mult = model.pixeloid_multiplier
                    self._draw_diamond_lines_to_surface(surface, sprite_x, sprite_y, scaled_bbox, current_sprite, pixeloid_mult, model)
                
                if current_sprite.detailed_analysis and self.show_raycast_analysis:
                    self._draw_analysis_points_to_surface(surface, sprite_x, sprite_y, scaled_bbox, current_sprite, model)

    def _draw_analysis_points_to_surface(self, surface: pygame.Surface, sprite_x, sprite_y, scaled_bbox, current_sprite, model: Optional[SpritesheetModel]):
        """Draw analysis points to the cached surface"""
        if not current_sprite.detailed_analysis or not model:
            return
        
        detailed_analysis = current_sprite.detailed_analysis
        pixeloid_mult = model.pixeloid_multiplier  # Cache for performance
        
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
                        if screen_x >= 0 and screen_x < self.DRAWING_AREA_WIDTH and screen_y >= 0 and screen_y < self.DRAWING_AREA_HEIGHT:
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
                        if screen_x >= 0 and screen_x < self.DRAWING_AREA_WIDTH and screen_y >= 0 and screen_y < self.DRAWING_AREA_HEIGHT:
                            pygame.draw.rect(surface, (255, 0, 255),  # Pink for all lines
                                           (screen_x, screen_y, pixeloid_mult, pixeloid_mult))
        
        # Draw midpoints (GREEN) - directly from Pydantic model
        for midpoint_name, midpoint in detailed_analysis.midpoints.items():
            if midpoint and (midpoint.x, midpoint.y) not in occupied_positions:
                screen_x = sprite_x + scaled_bbox.x + midpoint.x * pixeloid_mult
                screen_y = sprite_y + scaled_bbox.y + midpoint.y * pixeloid_mult
                # Only draw if within proper bounds
                if screen_x >= 0 and screen_x < self.DRAWING_AREA_WIDTH and screen_y >= 0 and screen_y < self.DRAWING_AREA_HEIGHT:
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
                if screen_x >= 0 and screen_x < self.DRAWING_AREA_WIDTH and screen_y >= 0 and screen_y < self.DRAWING_AREA_HEIGHT:
                    pygame.draw.rect(surface, (0, 0, 0),
                                   (screen_x, screen_y, pixeloid_mult, pixeloid_mult))
        
        # Draw special midpoint indicators when in midpoint mode
        if model.upper_lines_midpoint_mode and edge_contacts.bottom_from_left and edge_contacts.bottom_from_right:
            bottom_left = edge_contacts.bottom_from_left
            bottom_right = edge_contacts.bottom_from_right
            
            effective_upper_z = model.get_effective_upper_z_offset(model.current_sprite_index)
            mid_x = (bottom_left.x + bottom_right.x) // 2
            mid_y = effective_upper_z  # Use effective upper Z offset as top edge
            
            # Draw SW starting point (left of midpoint)
            sw_x = max(0, mid_x - 1)
            screen_x_sw = sprite_x + scaled_bbox.x + sw_x * pixeloid_mult
            screen_y = sprite_y + scaled_bbox.y + mid_y * pixeloid_mult
            
            if screen_x_sw >= 0 and screen_x_sw < self.DRAWING_AREA_WIDTH and screen_y >= 0 and screen_y < self.DRAWING_AREA_HEIGHT:
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
                
                if screen_x_se >= 0 and screen_x_se < self.DRAWING_AREA_WIDTH and screen_y >= 0 and screen_y < self.DRAWING_AREA_HEIGHT:
                    # Draw SE indicator in cyan with diagonal line
                    dot_size = max(pixeloid_mult * 2, 6)
                    center_x = screen_x_se + pixeloid_mult // 2
                    center_y = screen_y + pixeloid_mult // 2
                    
                    # Draw SE diagonal line (/)
                    pygame.draw.line(surface, (0, 255, 255),
                                   (center_x - dot_size//2, center_y + dot_size//2),
                                   (center_x + dot_size//2, center_y - dot_size//2), 2)
        
        # Draw diamond vertices if enabled OR if in manual vertex mode (independent of diamond lines)
        if (model.show_diamond_vertices or self.manual_vertex_mode) and current_sprite.diamond_info:
            self._draw_unified_diamond_vertices(surface, sprite_x, sprite_y, scaled_bbox, current_sprite, pixeloid_mult, model)
        
        # Draw custom keypoints if in custom keypoints mode
        if self.custom_keypoints_mode:
            self._draw_custom_keypoints(surface, sprite_x, sprite_y, current_sprite, pixeloid_mult, model)
    
    def _draw_unified_diamond_vertices(self, surface: pygame.Surface, sprite_x, sprite_y, scaled_bbox, current_sprite, pixeloid_mult, model: SpritesheetModel):
        """Single unified function to draw diamond vertices (both algorithmic and manual)"""
        if not current_sprite.diamond_info or not model:
            return
            
        diamond_info = current_sprite.diamond_info
        bbox = current_sprite.bbox
        if not bbox:
            return
            
        # Initialize font for vertex labels if not already done
        if not self._vertex_font:
            self._vertex_font = pygame.font.Font(None, max(12, pixeloid_mult + 2))
        
        # Get manual vertex overrides for current sprite
        sprite_key = model.current_sprite_index
        manual_overrides = self.manual_vertices.get(sprite_key, {})
        
        # Draw lower diamond vertices
        if diamond_info.lower_diamond:
            self._draw_diamond_level_vertices(
                surface, sprite_x, sprite_y, scaled_bbox, bbox, pixeloid_mult,
                'lower', diamond_info.lower_diamond, manual_overrides.get('lower', {}),
                False, model  # False = square vertices for lower
            )
        
        # Draw upper diamond vertices if present
        if diamond_info.upper_diamond:
            self._draw_diamond_level_vertices(
                surface, sprite_x, sprite_y, scaled_bbox, bbox, pixeloid_mult,
                'upper', diamond_info.upper_diamond, manual_overrides.get('upper', {}),
                True, model  # True = diamond vertices for upper
            )
    
    def _draw_diamond_level_vertices(self, surface, sprite_x, sprite_y, scaled_bbox, bbox, pixeloid_mult,
                                   diamond_level, diamond_data, manual_overrides, is_upper, model: SpritesheetModel):
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
            if not (0 <= screen_x < self.DRAWING_AREA_WIDTH and 0 <= screen_y < self.DRAWING_AREA_HEIGHT):
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
        if not self._vertex_font:
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
        label_x = max(0, min(label_x, self.DRAWING_AREA_WIDTH - text_rect.width))
        label_y = max(0, min(label_y, self.DRAWING_AREA_HEIGHT - text_rect.height))
        
        # Draw background rectangle for better text visibility
        bg_rect = pygame.Rect(label_x - 1, label_y - 1, text_rect.width + 2, text_rect.height + 2)
        pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect)  # Semi-transparent black background
        pygame.draw.rect(surface, (100, 100, 100), bg_rect, 1)  # Gray border
        
        # Draw the text
        surface.blit(text_surface, (label_x, label_y))
    
    def _draw_diamond_lines_to_surface(self, surface: pygame.Surface, sprite_x, sprite_y, scaled_bbox, current_sprite, pixeloid_mult, model: SpritesheetModel):
        """Draw blue diamond outline connecting vertices"""
        if not current_sprite.diamond_info or not model:
            return
            
        diamond_info = current_sprite.diamond_info
        bbox = current_sprite.bbox
        if not bbox:
            return
        
        # Get manual vertex overrides for current sprite
        sprite_key = model.current_sprite_index
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
                        if (screen_x >= 0 and screen_x < self.DRAWING_AREA_WIDTH and
                            screen_y >= 0 and screen_y < self.DRAWING_AREA_HEIGHT):
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

    def draw_analysis_points(self, screen: pygame.Surface, sprite_x, sprite_y, scaled_bbox, current_sprite, model: SpritesheetModel):
        """Draw analysis points (contact points, midpoints, isometric lines, convex hulls)"""
        if not current_sprite.detailed_analysis or not model:
            return
        
        detailed_analysis = current_sprite.detailed_analysis
        pixeloid_mult = model.pixeloid_multiplier  # Cache for performance
        
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
                        if screen_x >= self.LEFT_PANEL_WIDTH and screen_x < self.LEFT_PANEL_WIDTH + self.DRAWING_AREA_WIDTH:
                            hull_surface = pygame.Surface((pixeloid_mult, pixeloid_mult))
                            hull_surface.set_alpha(100)  # Semi-transparent
                            hull_surface.fill((0, 255, 0))  # Green for all hulls
                            screen.blit(hull_surface, (screen_x, screen_y))
        
        # Draw isometric lines (PINK) - directly from Pydantic model
        if detailed_analysis.isometric_analysis and detailed_analysis.isometric_analysis.lines:
            for direction, line_points in detailed_analysis.isometric_analysis.lines.items():
                for line_point in line_points:
                    if (line_point.x, line_point.y) not in occupied_positions:
                        screen_x = sprite_x + scaled_bbox.x + line_point.x * pixeloid_mult
                        screen_y = sprite_y + scaled_bbox.y + line_point.y * pixeloid_mult
                        # Only draw if within proper bounds (not over sidebars)
                        if screen_x >= self.LEFT_PANEL_WIDTH and screen_x < self.LEFT_PANEL_WIDTH + self.DRAWING_AREA_WIDTH:
                            pygame.draw.rect(screen, (255, 0, 255),  # Pink for all lines
                                           (screen_x, screen_y, pixeloid_mult, pixeloid_mult))
        
        # Draw midpoints (GREEN) - directly from Pydantic model
        for midpoint_name, midpoint in detailed_analysis.midpoints.items():
            if midpoint and (midpoint.x, midpoint.y) not in occupied_positions:
                screen_x = sprite_x + scaled_bbox.x + midpoint.x * pixeloid_mult
                screen_y = sprite_y + scaled_bbox.y + midpoint.y * pixeloid_mult
                # Only draw if within proper bounds (not over sidebars)
                if screen_x >= self.LEFT_PANEL_WIDTH and screen_x < self.LEFT_PANEL_WIDTH + self.DRAWING_AREA_WIDTH:
                    pygame.draw.rect(screen, (0, 255, 0),
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
                if screen_x >= self.LEFT_PANEL_WIDTH and screen_x < self.LEFT_PANEL_WIDTH + self.DRAWING_AREA_WIDTH:
                    pygame.draw.rect(screen, (0, 0, 0),
                                   (screen_x, screen_y, pixeloid_mult, pixeloid_mult))
        
        # Draw special midpoint indicators when in midpoint mode
        if model.upper_lines_midpoint_mode and edge_contacts.bottom_from_left and edge_contacts.bottom_from_right:
            bottom_left = edge_contacts.bottom_from_left
            bottom_right = edge_contacts.bottom_from_right
            
            effective_upper_z = model.get_effective_upper_z_offset(model.current_sprite_index)
            mid_x = (bottom_left.x + bottom_right.x) // 2
            mid_y = effective_upper_z  # Use effective upper Z offset as top edge
            
            # Draw SW starting point (left of midpoint)
            sw_x = max(0, mid_x - 1)
            screen_x_sw = sprite_x + scaled_bbox.x + sw_x * pixeloid_mult
            screen_y = sprite_y + scaled_bbox.y + mid_y * pixeloid_mult
            
            if screen_x_sw >= self.LEFT_PANEL_WIDTH and screen_x_sw < self.LEFT_PANEL_WIDTH + self.DRAWING_AREA_WIDTH:
                # Draw SW indicator in cyan with diagonal line
                dot_size = max(pixeloid_mult * 2, 6)
                center_x = screen_x_sw + pixeloid_mult // 2
                center_y = screen_y + pixeloid_mult // 2
                
                # Draw SW diagonal line (\)
                pygame.draw.line(screen, (0, 255, 255),
                               (center_x - dot_size//2, center_y - dot_size//2),
                               (center_x + dot_size//2, center_y + dot_size//2), 2)
            
            # Draw SE starting point (right of midpoint)
            bbox = current_sprite.bbox
            if bbox:
                se_x = min(bbox.width - 1, mid_x + 1)
                screen_x_se = sprite_x + scaled_bbox.x + se_x * pixeloid_mult
                
                if screen_x_se >= self.LEFT_PANEL_WIDTH and screen_x_se < self.LEFT_PANEL_WIDTH + self.DRAWING_AREA_WIDTH:
                    # Draw SE indicator in cyan with diagonal line
                    dot_size = max(pixeloid_mult * 2, 6)
                    center_x = screen_x_se + pixeloid_mult // 2
                    center_y = screen_y + pixeloid_mult // 2
                    
                    # Draw SE diagonal line (/)
                    pygame.draw.line(screen, (0, 255, 255),
                                   (center_x - dot_size//2, center_y + dot_size//2),
                                   (center_x + dot_size//2, center_y - dot_size//2), 2)
    
    def _get_vertex_name(self, vertex_num):
        """Get vertex name from number"""
        names = {1: 'North', 2: 'South', 3: 'East', 4: 'West'}
        return names.get(vertex_num, 'Unknown')
    
    def _draw_custom_keypoints(self, surface: pygame.Surface, sprite_x, sprite_y, current_sprite, pixeloid_mult, model: SpritesheetModel):
        """Draw custom keypoints with distinctive appearance and labels"""
        # Get keypoints from the model's sprite data (loaded from file) or renderer's dictionary (manual entry)
        sprite_key = model.current_sprite_index
        keypoints = {}
        
        # Priority: model's sprite data (from loaded file) > renderer's manual keypoints
        if current_sprite and current_sprite.custom_keypoints:
            keypoints.update({name: (point.x, point.y) for name, point in current_sprite.custom_keypoints.items()})
        
        # Add any manual keypoints from renderer (F3 mode additions)
        if sprite_key in self.custom_keypoints:
            keypoints.update(self.custom_keypoints[sprite_key])
        
        if not keypoints:
            return
        
        # Initialize font for keypoint labels if not already done
        if not self._vertex_font:
            self._vertex_font = pygame.font.Font(None, max(12, pixeloid_mult + 2))
        
        keypoint_size = max(pixeloid_mult + 2, 6)  # Slightly larger than vertices
        
        for keypoint_name, (abs_x, abs_y) in keypoints.items():
            # Convert absolute coordinates to screen coordinates
            screen_x = sprite_x + abs_x * pixeloid_mult
            screen_y = sprite_y + abs_y * pixeloid_mult
            
            # Check if within drawing area bounds
            if not (0 <= screen_x < self.DRAWING_AREA_WIDTH and 0 <= screen_y < self.DRAWING_AREA_HEIGHT):
                continue
            
            # Draw keypoint as a distinctive star shape in magenta
            self._draw_star_shape(surface, screen_x, screen_y, keypoint_size, (255, 0, 255))
            
            # Draw keypoint label
            self._draw_keypoint_label(surface, keypoint_name, screen_x, screen_y, keypoint_size)
    
    def _draw_star_shape(self, surface, x, y, size, color):
        """Draw a star shape for custom keypoints"""
        center_x = x + size // 2
        center_y = y + size // 2
        
        # Draw a 4-pointed star (cross + diagonal cross)
        half_size = size // 2
        
        # Main cross (+)
        pygame.draw.line(surface, color,
                        (center_x - half_size, center_y),
                        (center_x + half_size, center_y), 2)
        pygame.draw.line(surface, color,
                        (center_x, center_y - half_size),
                        (center_x, center_y + half_size), 2)
        
        # Diagonal cross (x)
        diagonal_offset = int(half_size * 0.7)  # Slightly smaller diagonals
        pygame.draw.line(surface, color,
                        (center_x - diagonal_offset, center_y - diagonal_offset),
                        (center_x + diagonal_offset, center_y + diagonal_offset), 2)
        pygame.draw.line(surface, color,
                        (center_x - diagonal_offset, center_y + diagonal_offset),
                        (center_x + diagonal_offset, center_y - diagonal_offset), 2)
    
    def _draw_keypoint_label(self, surface: pygame.Surface, label: str, keypoint_x: int, keypoint_y: int, keypoint_size: int):
        """Draw a text label for a custom keypoint"""
        if not self._vertex_font:
            return
        
        # Render the text
        text_surface = self._vertex_font.render(label, True, (255, 255, 255))  # White text
        text_rect = text_surface.get_rect()
        
        # Position label to the right and slightly below the keypoint
        label_x = keypoint_x + keypoint_size + 4
        label_y = keypoint_y + keypoint_size // 2 - text_rect.height // 2
        
        # Ensure label stays within drawing area bounds
        label_x = max(0, min(label_x, self.DRAWING_AREA_WIDTH - text_rect.width))
        label_y = max(0, min(label_y, self.DRAWING_AREA_HEIGHT - text_rect.height))
        
        # Draw background rectangle for better text visibility
        bg_rect = pygame.Rect(label_x - 1, label_y - 1, text_rect.width + 2, text_rect.height + 2)
        pygame.draw.rect(surface, (0, 0, 0, 200), bg_rect)  # Semi-transparent black background
        pygame.draw.rect(surface, (255, 0, 255), bg_rect, 1)  # Magenta border to match star
        
        # Draw the text
        surface.blit(text_surface, (label_x, label_y))