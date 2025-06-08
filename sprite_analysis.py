import pygame
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from spritesheet_model import (
    SpritesheetModel, SpriteData, BoundingBox, DiamondInfo, SingleDiamondData,
    EdgeContactPoints, IsometricAnalysis, DetailedAnalysis, Point, AssetType,
    point_from_tuple, points_from_list, bbox_from_pygame_rect
)

class SpriteAnalyzer:
    """Main class for analyzing sprites using the Pydantic model"""
    
    def __init__(self, model: SpritesheetModel):
        self.model = model
        self._spritesheet_surface: Optional[pygame.Surface] = None
        self._sprite_surfaces: List[pygame.Surface] = []
    
    def load_spritesheet_surface(self, surface: pygame.Surface):
        """Load the pygame surface for the spritesheet"""
        self._spritesheet_surface = surface
        self._extract_sprite_surfaces()
    
    def _extract_sprite_surfaces(self):
        """Extract individual sprite surfaces from the spritesheet"""
        if not self._spritesheet_surface:
            return
        
        self._sprite_surfaces = []
        for sprite_data in self.model.sprites:
            x, y, width, height = sprite_data.get_sprite_rect(self.model)
            sprite_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            sprite_surface.blit(self._spritesheet_surface, (0, 0), (x, y, width, height))
            self._sprite_surfaces.append(sprite_surface)
    
    def get_sprite_surface(self, sprite_index: int) -> Optional[pygame.Surface]:
        """Get the pygame surface for a specific sprite"""
        if 0 <= sprite_index < len(self._sprite_surfaces):
            return self._sprite_surfaces[sprite_index]
        return None
    
    def analyze_sprite(self, sprite_index: int) -> Optional[SpriteData]:
        """Analyze a single sprite and update its data"""
        if sprite_index >= len(self.model.sprites):
            return None
        
        sprite_data = self.model.sprites[sprite_index]
        sprite_surface = self.get_sprite_surface(sprite_index)
        
        if not sprite_surface:
            return None
        
        # Analyze basic properties
        pixel_count, bbox_rect = self._analyze_sprite_pixels(sprite_surface)
        sprite_data.pixel_count = pixel_count
        sprite_data.bbox = bbox_from_pygame_rect(bbox_rect)
        
        if sprite_data.bbox:
            # Perform detailed analysis first to get isometric lines
            sprite_data.detailed_analysis = self._analyze_detailed_measurements(
                sprite_surface, sprite_data.bbox, sprite_index
            )
            
            # Calculate diamond info using the already-computed isometric lines
            sprite_data.diamond_info = self._calculate_diamond_vertices_from_lines(
                sprite_data.bbox, sprite_index, sprite_data.detailed_analysis
            )
        
        return sprite_data
    
    def analyze_all_sprites(self):
        """Analyze all sprites in the spritesheet"""
        for i in range(len(self.model.sprites)):
            self.analyze_sprite(i)
    
    def _analyze_sprite_pixels(self, sprite: pygame.Surface) -> Tuple[int, Optional[pygame.Rect]]:
        """Analyze sprite for pixels above alpha threshold"""
        try:
            w, h = sprite.get_size()
            if w <= 0 or h <= 0:
                return 0, None
                
            # Get pixel array and create mask
            pixels = pygame.surfarray.pixels_alpha(sprite)
            mask = pixels > self.model.alpha_threshold
            pixel_count = np.sum(mask)
            
            # Find bounding box of pixels above threshold
            if pixel_count > 0:
                y_coords, x_coords = np.where(mask.T)
                
                if len(x_coords) > 0 and len(y_coords) > 0:
                    min_x = int(np.min(x_coords))
                    max_x = int(np.max(x_coords))
                    min_y = int(np.min(y_coords))
                    max_y = int(np.max(y_coords))
                    
                    # Calculate dimensions
                    width = max_x - min_x + 1
                    height = max_y - min_y + 1
                    
                    if width > 0 and height > 0:
                        bbox = pygame.Rect(min_x, min_y, width, height)
                        return int(pixel_count), bbox
            
            return int(pixel_count), None
            
        except Exception as e:
            print(f"Error analyzing sprite: {e}")
            return 0, None
    
    def _calculate_diamond_vertices_from_lines(self, bbox: BoundingBox, sprite_index: int, detailed_analysis: DetailedAnalysis) -> DiamondInfo:
        """Calculate diamond vertices using the already-computed isometric lines instead of duplicating work"""
        from spritesheet_model import SingleDiamondData, Point
        
        # Use frame-specific Z-offset
        effective_upper_z = self.model.get_effective_upper_z_offset(sprite_index)
        
        # Calculate legacy measurements for compatibility
        effective_height = bbox.height - effective_upper_z
        predicted_flat_height = bbox.width * 0.5
        diamond_height = effective_height - predicted_flat_height
        diamond_line_y = bbox.y + effective_upper_z + predicted_flat_height
        upper_z_line_y = bbox.y + effective_upper_z if effective_upper_z > 0 else None
        diamond_width = bbox.width
        lower_z_offset = predicted_flat_height
        
        # Extract vertices from already-computed isometric lines
        isometric_lines = detailed_analysis.isometric_analysis.lines if detailed_analysis.isometric_analysis else {}
        
        # Get bottom contact points (South vertex and starting points for NW/NE lines)
        bottom_left = detailed_analysis.edge_contact_points.bottom_from_left
        bottom_right = detailed_analysis.edge_contact_points.bottom_from_right
        
        if bottom_left and bottom_right:
            # South vertex: average of bottom left/right contact points in original coordinates
            south_x = bbox.x + (bottom_left.x + bottom_right.x) // 2
            south_y = bbox.y + max(bottom_left.y, bottom_right.y)  # Use the lower point
            
            # North vertex: Calculate from South using geometry (this is reliable)
            north_x = south_x
            north_y = south_y - bbox.width // 2
            
            # East/West vertices: Extract from isometric line endpoints (the actual raycast results!)
            east_x, east_y = bbox.x + bbox.width - 1, bbox.y + effective_upper_z + int(predicted_flat_height)  # fallback
            west_x, west_y = bbox.x, bbox.y + effective_upper_z + int(predicted_flat_height)  # fallback
            
            # Use actual raycast endpoints if available - CORRECT ASSIGNMENTS
            if 'NE' in isometric_lines and isometric_lines['NE']:
                # NE line goes from bottom_right toward NE, hits East edge = East vertex
                ne_line = isometric_lines['NE']
                if ne_line:
                    east_point = ne_line[-1]  # Last point in the line (bbox boundary hit)
                    east_x = bbox.x + east_point.x
                    east_y = bbox.y + east_point.y
            
            if 'NW' in isometric_lines and isometric_lines['NW']:
                # NW line goes from bottom_left toward NW, hits West edge = West vertex
                nw_line = isometric_lines['NW']
                if nw_line:
                    west_point = nw_line[-1]  # Last point in the line (bbox boundary hit)
                    west_x = bbox.x + west_point.x
                    west_y = bbox.y + west_point.y
        else:
            # Fallback to hardcoded calculation if contact points missing
            south_x = bbox.x + bbox.width // 2
            south_y = bbox.y + bbox.height - 1
            north_x = south_x
            north_y = south_y - bbox.width // 2
            east_x = bbox.x + bbox.width - 1
            east_y = bbox.y + effective_upper_z + int(predicted_flat_height)
            west_x = bbox.x
            west_y = east_y
        
        # Lower diamond center
        lower_center_x = bbox.x + bbox.width // 2
        lower_center_y = bbox.y + bbox.height // 2
        
        # Create lower diamond data using the extracted/computed vertices
        lower_diamond = SingleDiamondData(
            north_vertex=Point(x=north_x, y=north_y),
            south_vertex=Point(x=south_x, y=south_y),
            east_vertex=Point(x=east_x, y=east_y),
            west_vertex=Point(x=west_x, y=west_y),
            center=Point(x=lower_center_x, y=lower_center_y),
            z_offset=lower_z_offset
        )
        
        # Create upper diamond if there's a significant lower_z_offset (predicted_flat_height)
        upper_diamond = None
        if lower_z_offset > 0:  # Use lower_z_offset instead of effective_upper_z
            # Upper diamond is exactly like lower diamond but shifted up by diamond_height
            upper_north_x = north_x
            upper_north_y = north_y - int(diamond_height)
            
            upper_south_x = south_x
            upper_south_y = south_y - int(diamond_height)
            
            upper_east_x = east_x
            upper_east_y = east_y - int(diamond_height)
            
            upper_west_x = west_x
            upper_west_y = west_y - int(diamond_height)
            
            upper_center_x = lower_center_x
            upper_center_y = lower_center_y - int(diamond_height)
            
            upper_diamond = SingleDiamondData(
                north_vertex=Point(x=upper_north_x, y=upper_north_y),
                south_vertex=Point(x=upper_south_x, y=upper_south_y),
                east_vertex=Point(x=upper_east_x, y=upper_east_y),
                west_vertex=Point(x=upper_west_x, y=upper_west_y),
                center=Point(x=upper_center_x, y=upper_center_y),
                z_offset=effective_upper_z if effective_upper_z > 0 else lower_z_offset
            )
        
        return DiamondInfo(
            # Legacy fields
            diamond_height=diamond_height,
            predicted_flat_height=predicted_flat_height,
            effective_height=effective_height,
            line_y=diamond_line_y,
            upper_z_line_y=upper_z_line_y,
            # New explicit diamond data using raycast results
            lower_diamond=lower_diamond,
            upper_diamond=upper_diamond,
            diamond_width=diamond_width,
            lower_z_offset=lower_z_offset,
            upper_z_offset=effective_upper_z
        )
    
    def _analyze_detailed_measurements(self, sprite: pygame.Surface, bbox: BoundingBox, sprite_index: int) -> DetailedAnalysis:
        """Perform detailed geometric analysis of the sprite"""
        w, h = sprite.get_size()
        pixels = pygame.surfarray.pixels_alpha(sprite)
        mask = pixels > self.model.alpha_threshold
        
        # Use frame-specific Z-offset
        effective_upper_z = self.model.get_effective_upper_z_offset(sprite_index)
        
        # Calculate bbox edge midpoints (bbox-relative)
        effective_top_y = effective_upper_z
        midpoints = {
            'top': Point(x=bbox.width // 2, y=effective_top_y),
            'bottom': Point(x=bbox.width // 2, y=bbox.height - 1),
            'left': Point(x=0, y=bbox.height // 2),
            'right': Point(x=bbox.width - 1, y=bbox.height // 2)
        }
        
        # Find edge contact points
        edge_contact_points = self._find_edge_contact_points(bbox, mask, w, h, sprite_index)
        
        # Perform isometric analysis
        isometric_analysis = self._analyze_isometric_lines(bbox, mask, w, h, edge_contact_points, sprite_index)
        
        # Calculate enhanced data in original image space
        contact_points_data = self._calculate_enhanced_contact_data(bbox, mask, w, h, sprite_index, edge_contact_points, isometric_analysis)
        
        return DetailedAnalysis(
            midpoints=midpoints,
            edge_contact_points=edge_contact_points,
            isometric_analysis=isometric_analysis,
            corner_distances={},  # Legacy compatibility
            inter_pixel_distances={},  # Legacy compatibility
            contact_points_data=contact_points_data
        )
    
    def _find_edge_contact_points(self, bbox: BoundingBox, mask: np.ndarray, w: int, h: int, sprite_index: int) -> EdgeContactPoints:
        """Find contact points where sprite touches bounding box edges"""
        effective_upper_z = self.model.get_effective_upper_z_offset(sprite_index)
        effective_top_y = bbox.y + effective_upper_z
        
        def find_first_pixel_scan(start_range, scan_range, reverse_scan=False):
            for outer_coord in start_range:
                for inner_coord in (reversed(scan_range) if reverse_scan else scan_range):
                    x, y = outer_coord if isinstance(outer_coord, tuple) else (outer_coord, inner_coord)
                    if isinstance(outer_coord, tuple):
                        x, y = outer_coord[0], inner_coord
                    else:
                        x, y = outer_coord, inner_coord
                    
                    if x >= 0 and x < w and y >= 0 and y < h and mask[x, y]:
                        return Point(x=x - bbox.x, y=y - bbox.y)
            return None
        
        # TOP EDGE: scan from effective top
        top_from_left = None
        for y in range(effective_top_y, bbox.y + bbox.height):
            for x in range(bbox.x, bbox.x + bbox.width):
                if mask[x, y]:
                    top_from_left = Point(x=x - bbox.x, y=y - bbox.y)
                    break
            if top_from_left:
                break
        
        top_from_right = None
        for y in range(effective_top_y, bbox.y + bbox.height):
            for x in range(bbox.x + bbox.width - 1, bbox.x - 1, -1):
                if mask[x, y]:
                    top_from_right = Point(x=x - bbox.x, y=y - bbox.y)
                    break
            if top_from_right:
                break
        
        # BOTTOM EDGE: scan from bottom
        bottom_from_left = None
        for y in range(bbox.y + bbox.height - 1, bbox.y - 1, -1):
            for x in range(bbox.x, bbox.x + bbox.width):
                if mask[x, y]:
                    bottom_from_left = Point(x=x - bbox.x, y=y - bbox.y)
                    break
            if bottom_from_left:
                break
        
        bottom_from_right = None
        for y in range(bbox.y + bbox.height - 1, bbox.y - 1, -1):
            for x in range(bbox.x + bbox.width - 1, bbox.x - 1, -1):
                if mask[x, y]:
                    bottom_from_right = Point(x=x - bbox.x, y=y - bbox.y)
                    break
            if bottom_from_right:
                break
        
        # LEFT EDGE: scan from left
        left_from_top = None
        for x in range(bbox.x, bbox.x + bbox.width):
            for y in range(bbox.y, bbox.y + bbox.height):
                if mask[x, y]:
                    left_from_top = Point(x=x - bbox.x, y=y - bbox.y)
                    break
            if left_from_top:
                break
        
        left_from_bottom = None
        for x in range(bbox.x, bbox.x + bbox.width):
            for y in range(bbox.y + bbox.height - 1, bbox.y - 1, -1):
                if mask[x, y]:
                    left_from_bottom = Point(x=x - bbox.x, y=y - bbox.y)
                    break
            if left_from_bottom:
                break
        
        # RIGHT EDGE: scan from right
        right_from_top = None
        for x in range(bbox.x + bbox.width - 1, bbox.x - 1, -1):
            for y in range(bbox.y, bbox.y + bbox.height):
                if mask[x, y]:
                    right_from_top = Point(x=x - bbox.x, y=y - bbox.y)
                    break
            if right_from_top:
                break
        
        right_from_bottom = None
        for x in range(bbox.x + bbox.width - 1, bbox.x - 1, -1):
            for y in range(bbox.y + bbox.height - 1, bbox.y - 1, -1):
                if mask[x, y]:
                    right_from_bottom = Point(x=x - bbox.x, y=y - bbox.y)
                    break
            if right_from_bottom:
                break
        
        return EdgeContactPoints(
            top_from_left=top_from_left,
            top_from_right=top_from_right,
            bottom_from_left=bottom_from_left,
            bottom_from_right=bottom_from_right,
            left_from_top=left_from_top,
            left_from_bottom=left_from_bottom,
            right_from_top=right_from_top,
            right_from_bottom=right_from_bottom
        )
    
    def _analyze_isometric_lines(self, bbox: BoundingBox, mask: np.ndarray, w: int, h: int,
                                edge_contact_points: EdgeContactPoints, sprite_index: int) -> IsometricAnalysis:
        """Analyze isometric lines and convex hulls"""
        lines = {}
        convex_hulls = {}
        effective_upper_z = self.model.get_effective_upper_z_offset(sprite_index)
        
        # Bottom lines always use actual contact points
        if edge_contact_points.bottom_from_left:
            start_pos = edge_contact_points.bottom_from_left
            start_x = bbox.x + start_pos.x
            start_y = bbox.y + start_pos.y
            line_nw = self._trace_isometric_line(start_x, start_y, 'NW', bbox, mask, w, h)
            lines['NW'] = points_from_list(line_nw)
        
        if edge_contact_points.bottom_from_right:
            start_pos = edge_contact_points.bottom_from_right
            start_x = bbox.x + start_pos.x
            start_y = bbox.y + start_pos.y
            line_ne = self._trace_isometric_line(start_x, start_y, 'NE', bbox, mask, w, h)
            lines['NE'] = points_from_list(line_ne)
        
        # Top lines: use midpoint mode if enabled
        if self.model.upper_lines_midpoint_mode:
            if edge_contact_points.bottom_from_left and edge_contact_points.bottom_from_right:
                mid_x = (edge_contact_points.bottom_from_left.x + edge_contact_points.bottom_from_right.x) // 2
                start_y = bbox.y + effective_upper_z
                
                # SW from one pixel left of midpoint
                start_x_sw = bbox.x + max(0, mid_x - 1)
                line_sw = self._trace_isometric_line(start_x_sw, start_y, 'SW', bbox, mask, w, h)
                lines['SW'] = points_from_list(line_sw)
                
                # SE from one pixel right of midpoint
                start_x_se = bbox.x + min(bbox.width - 1, mid_x + 1)
                line_se = self._trace_isometric_line(start_x_se, start_y, 'SE', bbox, mask, w, h)
                lines['SE'] = points_from_list(line_se)
        else:
            # Default mode: use actual top contact points
            if edge_contact_points.top_from_left:
                start_pos = edge_contact_points.top_from_left
                start_x = bbox.x + start_pos.x
                start_y = bbox.y + start_pos.y
                line_sw = self._trace_isometric_line(start_x, start_y, 'SW', bbox, mask, w, h)
                lines['SW'] = points_from_list(line_sw)
            
            if edge_contact_points.top_from_right:
                start_pos = edge_contact_points.top_from_right
                start_x = bbox.x + start_pos.x
                start_y = bbox.y + start_pos.y
                line_se = self._trace_isometric_line(start_x, start_y, 'SE', bbox, mask, w, h)
                lines['SE'] = points_from_list(line_se)
        
        # Calculate convex hulls for each direction
        for direction, line_points in lines.items():
            hull_points = self._calculate_convex_hull_for_line(
                [(p.x, p.y) for p in line_points], direction, bbox, mask, w, h, sprite_index
            )
            convex_hulls[direction] = points_from_list(hull_points)
        
        # Combine all points for legacy compatibility
        all_line_points = []
        all_hull_points = []
        
        for line_points in lines.values():
            all_line_points.extend(line_points)
        
        for hull_points in convex_hulls.values():
            all_hull_points.extend(hull_points)
        
        return IsometricAnalysis(
            lines=lines,
            convex_hulls=convex_hulls,
            line_points=list(set(all_line_points)),
            convex_hull_area=list(set(all_hull_points))
        )
    
    def _trace_isometric_line(self, start_x: int, start_y: int, direction: str, 
                             bbox: BoundingBox, mask: np.ndarray, w: int, h: int) -> List[Tuple[int, int]]:
        """Trace an isometric line in the specified direction"""
        points = []
        x, y = start_x, start_y
        step = 0
        
        # Define movement patterns for each direction
        if direction == 'NW':
            moves = [(-1, -1), (-1, 0)]
        elif direction == 'NE':
            moves = [(1, -1), (1, 0)]
        elif direction == 'SW':
            moves = [(-1, 1), (-1, 0)]
        elif direction == 'SE':
            moves = [(1, 1), (1, 0)]
        else:
            return points
        
        # Add the starting point first
        if (x >= bbox.x and x < bbox.x + bbox.width and 
            y >= bbox.y and y < bbox.y + bbox.height):
            rel_x = x - bbox.x
            rel_y = y - bbox.y
            points.append((rel_x, rel_y))
        
        # Trace the line until we hit the bbox edge
        while True:
            dx, dy = moves[step % 2]
            x += dx
            y += dy
            step += 1
            
            if not (x >= bbox.x and x < bbox.x + bbox.width and 
                    y >= bbox.y and y < bbox.y + bbox.height):
                break
                
            rel_x = x - bbox.x
            rel_y = y - bbox.y
            points.append((rel_x, rel_y))
        
        return points
    
    def _calculate_convex_hull_for_line(self, line_points: List[Tuple[int, int]], direction: str,
                                       bbox: BoundingBox, mask: np.ndarray, w: int, h: int, sprite_index: int) -> List[Tuple[int, int]]:
        """Calculate the convex hull area between an isometric line and the sprite edge"""
        hull_points = []
        line_points_dict = {point[0]: point[1] for point in line_points}
        effective_upper_z = self.model.get_effective_upper_z_offset(sprite_index)
        
        if direction in ['NW', 'NE']:
            # For lines going up from bottom, scan from bottom to find sprite edge
            for check_x in line_points_dict:
                line_y = line_points_dict[check_x]
                
                first_pixel_y = None
                for check_y in range(bbox.height - 1, -1, -1):
                    check_x_global = bbox.x + check_x
                    check_y_global = bbox.y + check_y
                    if (check_x_global >= 0 and check_x_global < w and
                        check_y_global >= 0 and check_y_global < h and
                        mask[check_x_global, check_y_global]):
                        first_pixel_y = check_y
                        break
                
                if first_pixel_y is not None and first_pixel_y < line_y:
                    for fill_y in range(first_pixel_y + 1, line_y):
                        hull_points.append((check_x, fill_y))
        
        else:  # direction in ['SW', 'SE']
            # For lines going down from top, scan from effective top
            for check_x in line_points_dict:
                line_y = line_points_dict[check_x]
                
                first_pixel_y = None
                start_scan_y = effective_upper_z
                for check_y in range(start_scan_y, bbox.height):
                    check_x_global = bbox.x + check_x
                    check_y_global = bbox.y + check_y
                    if (check_x_global >= 0 and check_x_global < w and
                        check_y_global >= 0 and check_y_global < h and
                        mask[check_x_global, check_y_global]):
                        first_pixel_y = check_y
                        break
                
                if first_pixel_y is not None and first_pixel_y > line_y:
                    for fill_y in range(line_y + 1, first_pixel_y):
                        hull_points.append((check_x, fill_y))
        
        return hull_points
    
    def _calculate_enhanced_contact_data(self, bbox: BoundingBox, mask: np.ndarray, w: int, h: int,
                                       sprite_index: int, edge_contact_points: EdgeContactPoints,
                                       isometric_analysis: IsometricAnalysis):
        """Calculate enhanced contact data in original image space"""
        from spritesheet_model import ContactPointsData, LineData, EdgeContactPoints as OriginalEdgeContactPoints
        
        # Convert edge contact points to original image space
        def convert_to_original(point: Optional[Point]) -> Optional[Point]:
            if point:
                return Point(x=bbox.x + point.x, y=bbox.y + point.y)
            return None
        
        edge_contacts_original = OriginalEdgeContactPoints(
            top_from_left=convert_to_original(edge_contact_points.top_from_left),
            top_from_right=convert_to_original(edge_contact_points.top_from_right),
            bottom_from_left=convert_to_original(edge_contact_points.bottom_from_left),
            bottom_from_right=convert_to_original(edge_contact_points.bottom_from_right),
            left_from_top=convert_to_original(edge_contact_points.left_from_top),
            left_from_bottom=convert_to_original(edge_contact_points.left_from_bottom),
            right_from_top=convert_to_original(edge_contact_points.right_from_top),
            right_from_bottom=convert_to_original(edge_contact_points.right_from_bottom)
        )
        
        # Convert midpoints to original image space
        effective_upper_z = self.model.get_effective_upper_z_offset(sprite_index)
        midpoints_original = {
            'top': Point(x=bbox.x + bbox.width // 2, y=bbox.y + effective_upper_z),
            'bottom': Point(x=bbox.x + bbox.width // 2, y=bbox.y + bbox.height - 1),
            'left': Point(x=bbox.x, y=bbox.y + bbox.height // 2),
            'right': Point(x=bbox.x + bbox.width - 1, y=bbox.y + bbox.height // 2)
        }
        
        # Calculate line data for both modes
        upper_line_data = LineData()
        lower_line_data = LineData()
        
        # Convert current lines to original space
        current_mode = "midpoint_mode" if self.model.upper_lines_midpoint_mode else "contact_points_mode"
        for direction, line_points in isometric_analysis.lines.items():
            converted_points = [Point(x=bbox.x + p.x, y=bbox.y + p.y) for p in line_points]
            if direction in ['SW', 'SE']:  # Upper lines
                setattr(upper_line_data, current_mode, {**getattr(upper_line_data, current_mode), direction: converted_points})
            else:  # Lower lines (NW, NE)
                setattr(lower_line_data, current_mode, {**getattr(lower_line_data, current_mode), direction: converted_points})
        
        # TODO: Calculate lines for the other mode as well (contact_points vs midpoint)
        # This would require running the analysis in both modes
        
        return ContactPointsData(
            edge_contacts_original=edge_contacts_original,
            midpoints_original=midpoints_original,
            upper_line_data=upper_line_data,
            lower_line_data=lower_line_data
        )