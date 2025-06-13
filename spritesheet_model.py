from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import json
from pathlib import Path

class AssetType(str, Enum):
    """
    Type of isometric asset for procedural generation pipeline.
    
    Used to categorize sprites for different algorithmic processing:
    - TILE: Standard isometric blocks with upper and lower diamonds
    - WALL: Vertical wall segments
    - DOOR: Interactive door elements
    - STAIR: Step/stair elements with elevation changes
    """
    TILE = "tile"
    WALL = "wall"
    DOOR = "door"
    STAIR = "stair"

class EdgeProperty(str, Enum):
    """
    Edge properties for line of sight and movement blocking.
    
    Used to define how edges of sub-diamonds affect game mechanics:
    - NONE: Edge has no blocking properties (default/unset)
    - BLOCKS: Edge blocks both line of sight and movement
    - TRANSPARENT: Edge allows line of sight but blocks movement
    - PASSABLE: Edge allows both line of sight and movement
    """
    NONE = "none"
    BLOCKS = "blocks"
    TRANSPARENT = "transparent"
    PASSABLE = "passable"

class EdgeProperties(BaseModel):
    """
    Properties for an edge defining its interaction with game mechanics.
    
    Each edge can independently control line of sight and movement blocking
    for fine-grained control over game mechanics like walls, windows, etc.
    """
    blocks_line_of_sight: Optional[bool] = Field(
        default=None,
        description="Whether this edge blocks line of sight (None=unset, True=blocks, False=transparent)"
    )
    blocks_movement: Optional[bool] = Field(
        default=None,
        description="Whether this edge blocks movement (None=unset, True=blocks, False=passable)"
    )
    
    def get_combined_property(self) -> EdgeProperty:
        """Get the combined edge property enum value"""
        if self.blocks_line_of_sight is None and self.blocks_movement is None:
            return EdgeProperty.NONE
        elif self.blocks_line_of_sight is True and self.blocks_movement is True:
            return EdgeProperty.BLOCKS
        elif self.blocks_line_of_sight is False and self.blocks_movement is True:
            return EdgeProperty.TRANSPARENT
        elif self.blocks_line_of_sight is False and self.blocks_movement is False:
            return EdgeProperty.PASSABLE
        else:
            # Mixed or partial settings - default to blocks for safety
            return EdgeProperty.BLOCKS

class Point(BaseModel):
    """
    A 2D point representing a pixel coordinate in the sprite analysis.
    
    Used throughout the diamond tile analysis to mark significant geometric features
    such as contact points where the diamond touches edges, vertices of isometric lines,
    and boundaries of convex hull regions.
    """
    x: int = Field(..., description="Horizontal pixel coordinate (0-based, left to right)")
    y: int = Field(..., description="Vertical pixel coordinate (0-based, top to bottom)")
    
    def __hash__(self):
        """Make Point hashable for use in sets and as dict keys"""
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        """Equality comparison for Point objects"""
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y

class SubDiamondData(BaseModel):
    """
    Data for a single sub-diamond quadrant within a main diamond.
    
    Each main diamond contains 4 sub-diamonds (North, South, East, West quadrants)
    that divide the isometric tile for granular game mechanics control.
    
    Sub-diamonds are proper diamond shapes with 4 vertices, just like the main diamond.
    Each has its own edge properties for the 4 edges of the diamond.
    """
    quadrant: str = Field(..., description="Quadrant name: 'north', 'south', 'east', or 'west'")
    
    # Vertices defining this sub-diamond (proper diamond shape with 4 corners)
    north_vertex: Point = Field(..., description="North corner of this sub-diamond")
    south_vertex: Point = Field(..., description="South corner of this sub-diamond")
    east_vertex: Point = Field(..., description="East corner of this sub-diamond")
    west_vertex: Point = Field(..., description="West corner of this sub-diamond")
    center: Point = Field(..., description="Center point of this sub-diamond")
    
    # Gameplay properties
    is_walkable: Optional[bool] = Field(
        default=None,
        description="Whether this sub-diamond surface is walkable (None=unset, True=floor, False=block)"
    )
    
    # Edge properties for this sub-diamond's 4 edges
    north_west_edge: EdgeProperties = Field(
        default_factory=EdgeProperties,
        description="Properties for the north-west edge of this sub-diamond"
    )
    north_east_edge: EdgeProperties = Field(
        default_factory=EdgeProperties,
        description="Properties for the north-east edge of this sub-diamond"
    )
    south_west_edge: EdgeProperties = Field(
        default_factory=EdgeProperties,
        description="Properties for the south-west edge of this sub-diamond"
    )
    south_east_edge: EdgeProperties = Field(
        default_factory=EdgeProperties,
        description="Properties for the south-east edge of this sub-diamond"
    )

class BoundingBox(BaseModel):
    """
    A rectangular bounding box defining the minimal rectangle containing all non-transparent pixels.
    
    For diamond tiles, this represents the tight crop area around the entire diamond shape,
    including both the main diamond body and any upper diamond extensions.
    """
    x: int = Field(..., description="Left edge pixel coordinate of the bounding box")
    y: int = Field(..., description="Top edge pixel coordinate of the bounding box")
    width: int = Field(..., description="Width of the bounding box in pixels")
    height: int = Field(..., description="Height of the bounding box in pixels")

class SingleDiamondData(BaseModel):
    """
    Geometric data for a single isometric diamond (upper or lower).
    
    Contains the essential procedural generation data:
    - Four corner vertices (north, south, east, west) in original sprite coordinates
    - Diamond center point for positioning calculations
    - Z-offset for elevation relative to sprite base
    """
    north_vertex: Point = Field(..., description="North corner of the diamond (top point)")
    south_vertex: Point = Field(..., description="South corner of the diamond (bottom point)")
    east_vertex: Point = Field(..., description="East corner of the diamond (right point)")
    west_vertex: Point = Field(..., description="West corner of the diamond (left point)")
    center: Point = Field(..., description="Center point of the diamond for positioning")
    z_offset: float = Field(..., description="Z elevation offset from sprite base in pixels")
    
    # NEW: Optional midpoints (won't break existing code)
    north_east_midpoint: Optional[Point] = Field(default=None, description="Midpoint between north and east vertices")
    east_south_midpoint: Optional[Point] = Field(default=None, description="Midpoint between east and south vertices")
    south_west_midpoint: Optional[Point] = Field(default=None, description="Midpoint between south and west vertices")
    west_north_midpoint: Optional[Point] = Field(default=None, description="Midpoint between west and north vertices")

class GameplayDiamondData(BaseModel):
    """
    Extended diamond data with gameplay mechanics for isometric grid placement.
    
    Includes all geometric data from SingleDiamondData plus:
    - 4 sub-diamonds (quadrants) for granular game mechanics
    - Edge properties for line of sight and movement blocking
    - Surface walkability per sub-diamond
    """
    # Core geometric data (same as SingleDiamondData)
    north_vertex: Point = Field(..., description="North corner of the diamond (top point)")
    south_vertex: Point = Field(..., description="South corner of the diamond (bottom point)")
    east_vertex: Point = Field(..., description="East corner of the diamond (right point)")
    west_vertex: Point = Field(..., description="West corner of the diamond (left point)")
    center: Point = Field(..., description="Center point of the diamond for positioning")
    z_offset: float = Field(..., description="Z elevation offset from sprite base in pixels")
    
    # Midpoints (required for sub-diamond calculation)
    north_east_midpoint: Optional[Point] = Field(default=None, description="Midpoint between north and east vertices")
    east_south_midpoint: Optional[Point] = Field(default=None, description="Midpoint between east and south vertices")
    south_west_midpoint: Optional[Point] = Field(default=None, description="Midpoint between south and west vertices")
    west_north_midpoint: Optional[Point] = Field(default=None, description="Midpoint between west and north vertices")
    
    # Gameplay mechanics
    sub_diamonds: Dict[str, SubDiamondData] = Field(
        default_factory=dict,
        description="4 sub-diamond quadrants (north, south, east, west) for granular game mechanics"
    )
    
    @classmethod
    def from_single_diamond(cls, single_diamond: SingleDiamondData) -> 'GameplayDiamondData':
        """Create gameplay diamond from existing SingleDiamondData"""
        gameplay_diamond = cls(
            north_vertex=single_diamond.north_vertex,
            south_vertex=single_diamond.south_vertex,
            east_vertex=single_diamond.east_vertex,
            west_vertex=single_diamond.west_vertex,
            center=single_diamond.center,
            z_offset=single_diamond.z_offset,
            north_east_midpoint=single_diamond.north_east_midpoint,
            east_south_midpoint=single_diamond.east_south_midpoint,
            south_west_midpoint=single_diamond.south_west_midpoint,
            west_north_midpoint=single_diamond.west_north_midpoint
        )
        
        # Initialize sub-diamonds and edges if midpoints are available
        if all([
            single_diamond.north_east_midpoint,
            single_diamond.east_south_midpoint,
            single_diamond.south_west_midpoint,
            single_diamond.west_north_midpoint
        ]):
            gameplay_diamond._initialize_sub_diamonds_and_edges()
        
        return gameplay_diamond
    
    def _initialize_sub_diamonds_and_edges(self):
        """Initialize the 4 sub-diamonds and their edge properties"""
        # Calculate midpoints if they don't exist
        self._ensure_midpoints_calculated()
        
        if not all([self.north_east_midpoint, self.east_south_midpoint,
                   self.south_west_midpoint, self.west_north_midpoint]):
            return
        
        # Type assertions - we know these are not None due to the check above
        assert self.north_east_midpoint is not None
        assert self.east_south_midpoint is not None
        assert self.south_west_midpoint is not None
        assert self.west_north_midpoint is not None
            
        # Calculate the true geometric center of the main diamond (intersection of diagonals)
        true_center = Point(
            x=(self.north_vertex.x + self.south_vertex.x) // 2,
            y=(self.north_vertex.y + self.south_vertex.y) // 2
        )
        
        # Create sub-diamonds for each quadrant - each is a proper diamond with 4 vertices
        self.sub_diamonds = {
            'north': SubDiamondData(
                quadrant='north',
                north_vertex=self.north_vertex,          # Main vertex (tip of the quadrant)
                south_vertex=true_center,                # True center of main diamond
                east_vertex=self.north_east_midpoint,    # Midpoint to east
                west_vertex=self.west_north_midpoint,    # Midpoint to west
                center=Point(  # Center of this sub-diamond
                    x=(self.north_vertex.x + true_center.x) // 2,
                    y=(self.north_vertex.y + true_center.y) // 2
                )
            ),
            'south': SubDiamondData(
                quadrant='south',
                north_vertex=true_center,               # True center of main diamond
                south_vertex=self.south_vertex,         # Main vertex (tip of the quadrant)
                east_vertex=self.east_south_midpoint,   # Midpoint to east
                west_vertex=self.south_west_midpoint,   # Midpoint to west
                center=Point(  # Center of this sub-diamond
                    x=(self.south_vertex.x + true_center.x) // 2,
                    y=(self.south_vertex.y + true_center.y) // 2
                )
            ),
            'east': SubDiamondData(
                quadrant='east',
                north_vertex=self.north_east_midpoint,  # Midpoint to north
                south_vertex=self.east_south_midpoint,  # Midpoint to south
                east_vertex=self.east_vertex,           # Main vertex (tip of the quadrant)
                west_vertex=true_center,                # True center of main diamond
                center=Point(  # Center of this sub-diamond
                    x=(self.east_vertex.x + true_center.x) // 2,
                    y=(self.east_vertex.y + true_center.y) // 2
                )
            ),
            'west': SubDiamondData(
                quadrant='west',
                north_vertex=self.west_north_midpoint,  # Midpoint to north
                south_vertex=self.south_west_midpoint,  # Midpoint to south
                east_vertex=true_center,                # True center of main diamond
                west_vertex=self.west_vertex,           # Main vertex (tip of the quadrant)
                center=Point(  # Center of this sub-diamond
                    x=(self.west_vertex.x + true_center.x) // 2,
                    y=(self.west_vertex.y + true_center.y) // 2
                )
            )
        }
    
    def _ensure_midpoints_calculated(self):
        """Ensure midpoints are calculated between diamond vertices"""
        # Calculate midpoints if they don't exist
        if not self.north_east_midpoint:
            self.north_east_midpoint = Point(
                x=(self.north_vertex.x + self.east_vertex.x) // 2,
                y=(self.north_vertex.y + self.east_vertex.y) // 2
            )
        
        if not self.east_south_midpoint:
            self.east_south_midpoint = Point(
                x=(self.east_vertex.x + self.south_vertex.x) // 2,
                y=(self.east_vertex.y + self.south_vertex.y) // 2
            )
        
        if not self.south_west_midpoint:
            self.south_west_midpoint = Point(
                x=(self.south_vertex.x + self.west_vertex.x) // 2,
                y=(self.south_vertex.y + self.west_vertex.y) // 2
            )
        
        if not self.west_north_midpoint:
            self.west_north_midpoint = Point(
                x=(self.west_vertex.x + self.north_vertex.x) // 2,
                y=(self.west_vertex.y + self.north_vertex.y) // 2
            )
    
    def ensure_sub_diamonds_initialized(self):
        """Public method to ensure sub-diamonds are properly initialized"""
        if not self.sub_diamonds:
            self._initialize_sub_diamonds_and_edges()
    
    def set_sub_diamond_walkability(self, quadrant: str, is_walkable: bool):
        """Set walkability for a specific sub-diamond quadrant"""
        if quadrant in self.sub_diamonds:
            self.sub_diamonds[quadrant].is_walkable = is_walkable
    
    def get_walkable_quadrants(self) -> List[str]:
        """Get list of walkable quadrant names"""
        return [
            quadrant for quadrant, data in self.sub_diamonds.items()
            if data.is_walkable is True
        ]
    
    def set_sub_diamond_edge_property(self, quadrant: str, edge: str, blocks_line_of_sight: Optional[bool] = None,
                                    blocks_movement: Optional[bool] = None):
        """Set properties for a specific sub-diamond edge"""
        if quadrant in self.sub_diamonds:
            sub_diamond = self.sub_diamonds[quadrant]
            edge_attr = f"{edge}_edge"
            if hasattr(sub_diamond, edge_attr):
                edge_props = getattr(sub_diamond, edge_attr)
                if blocks_line_of_sight is not None:
                    edge_props.blocks_line_of_sight = blocks_line_of_sight
                if blocks_movement is not None:
                    edge_props.blocks_movement = blocks_movement

class DiamondInfo(BaseModel):
    """
    Complete geometric analysis of the two-diamond isometric tile structure.
    
    For isometric tiles/blocks, this provides explicit vertex coordinates and geometric data
    for both the lower diamond (main structure) and upper diamond (elevated section).
    
    Key outputs for procedural algorithms:
    - Precise 4-corner vertices for each diamond in original sprite coordinates
    - Diamond centers for positioning and alignment
    - Z-offsets for elevation calculations
    - Relationship data between upper and lower structures
    """
    # Legacy measurements (kept for compatibility)
    diamond_height: float = Field(..., description="Height in pixels of the diamond-shaped top surface (slanted edges)")
    predicted_flat_height: float = Field(..., description="Height in pixels of the flat vertical sides below the diamond top")
    effective_height: float = Field(..., description="Total effective height combining diamond and flat portions")
    line_y: float = Field(..., description="Y-coordinate where the diamond top meets the flat sides (relative to bounding box)")
    upper_z_line_y: Optional[float] = Field(None, description="Y-coordinate of the upper diamond separation line when upper_z_offset is used")
    
    # New explicit diamond data for procedural generation
    lower_diamond: GameplayDiamondData = Field(..., description="Lower diamond structure with vertices, center, and z-offset (always 0)")
    upper_diamond: Optional[GameplayDiamondData] = Field(None, description="Upper diamond structure (when upper_z_offset > 0)")
    extra_diamonds: Dict[str, GameplayDiamondData] = Field(default_factory=dict, description="Custom named diamonds with their own z-offsets")
    
    # Derived measurements
    diamond_width: float = Field(..., description="Width of the diamond (distance between east and west vertices)")
    lower_z_offset: float = Field(..., description="Z-offset of the lower diamond base from sprite bottom (legacy compatibility)")
    upper_z_offset: float = Field(default=0, description="Z-offset of the upper diamond from sprite top (legacy compatibility)")
    diamonds_z_offset: Optional[float] = Field(default=None, description="Actual measured Y-axis difference between north vertices of lower and upper diamonds (isometric height)")

class EdgeContactPoints(BaseModel):
    """
    Contact points where the diamond sprite content touches the edges of its bounding box.
    
    For diamond tiles, these points define the extremities of the diamond shape:
    - Top contacts: Peak vertices of the upper diamond edges
    - Bottom contacts: Lower vertices where the diamond sides meet the base
    - Left/Right contacts: Leftmost and rightmost points of the diamond's horizontal extent
    
    These points are crucial for understanding the diamond's geometric boundaries and
    for generating accurate isometric line traces.
    """
    top_from_left: Optional[Point] = Field(default=None, description="Topmost pixel found by scanning from left edge")
    top_from_right: Optional[Point] = Field(default=None, description="Topmost pixel found by scanning from right edge")
    bottom_from_left: Optional[Point] = Field(default=None, description="Bottommost pixel found by scanning from left edge")
    bottom_from_right: Optional[Point] = Field(default=None, description="Bottommost pixel found by scanning from right edge")
    left_from_top: Optional[Point] = Field(default=None, description="Leftmost pixel found by scanning from top edge")
    left_from_bottom: Optional[Point] = Field(default=None, description="Leftmost pixel found by scanning from bottom edge")
    right_from_top: Optional[Point] = Field(default=None, description="Rightmost pixel found by scanning from top edge")
    right_from_bottom: Optional[Point] = Field(default=None, description="Rightmost pixel found by scanning from bottom edge")

class IsometricAnalysis(BaseModel):
    """
    Analysis of isometric diagonal lines that form the diamond tile's structure.
    
    Diamond tiles have four main diagonal directions:
    - NW (Northwest): Upper-left slanted edges of the diamond
    - NE (Northeast): Upper-right slanted edges of the diamond
    - SW (Southwest): Lower-left slanted edges of the diamond
    - SE (Southeast): Lower-right slanted edges of the diamond
    
    These lines trace the contours of the diamond shape and help define its 3D structure.
    Convex hulls represent the filled regions bounded by these diagonal edges.
    """
    lines: Dict[str, List[Point]] = Field(
        default_factory=dict,
        description="Isometric line traces for each direction (NW/NE/SW/SE). Each direction contains ordered points tracing the diagonal edges of the diamond structure."
    )
    convex_hulls: Dict[str, List[Point]] = Field(
        default_factory=dict,
        description="Convex hull boundaries for each direction. Defines the filled polygonal regions bounded by the isometric lines, representing solid areas of the diamond."
    )
    line_points: List[Point] = Field(
        default_factory=list,
        description="Legacy field: Combined list of all isometric line points (deprecated, use 'lines' instead)"
    )
    convex_hull_area: List[Point] = Field(
        default_factory=list,
        description="Legacy field: Combined convex hull area points (deprecated, use 'convex_hulls' instead)"
    )
    
    # Compact format for JSON serialization (optional)
    line_segments: Optional[Dict[str, Tuple[Point, Point]]] = Field(
        default=None, exclude=True,
        description="Compact JSON representation: start and end points of each line direction (excludes intermediate points)"
    )
    hull_bounds: Optional[Dict[str, Tuple[Point, Point]]] = Field(
        default=None, exclude=True,
        description="Compact JSON representation: min/max boundary points of each convex hull (excludes full polygon)"
    )

class LineData(BaseModel):
    """
    Isometric line data for both analysis modes, supporting the two-diamond structure.
    
    Two modes for generating upper isometric lines in diamond tiles:
    1. Contact Points Mode: Lines start from the actual edge contact points where the diamond touches the bounding box
    2. Midpoint Mode: Lines start from calculated midpoints, useful when upper_z_offset creates a second diamond layer
    
    This enables analysis of both the main diamond and any upper diamond extensions.
    """
    contact_points_mode: Dict[str, List[Point]] = Field(
        default_factory=dict,
        description="Isometric lines (NW/NE/SW/SE) starting from edge contact points. Used for analyzing the main diamond structure."
    )
    midpoint_mode: Dict[str, List[Point]] = Field(
        default_factory=dict,
        description="Isometric lines (NW/NE/SW/SE) starting from calculated midpoints. Used when upper_z_offset creates an upper diamond layer."
    )
    
    # Compact format for JSON serialization (optional)
    contact_points_segments: Optional[Dict[str, Tuple[Point, Point]]] = Field(
        default=None, exclude=True,
        description="Compact JSON representation of contact_points_mode lines (start/end points only)"
    )
    midpoint_segments: Optional[Dict[str, Tuple[Point, Point]]] = Field(
        default=None, exclude=True,
        description="Compact JSON representation of midpoint_mode lines (start/end points only)"
    )
    
class ContactPointsData(BaseModel):
    """
    Comprehensive contact point analysis data in original sprite coordinate space.
    
    Contains both the raw contact points and the derived isometric line analysis
    for the complete two-diamond structure (main diamond + optional upper diamond).
    """
    edge_contacts_original: EdgeContactPoints = Field(
        default=EdgeContactPoints(),
        description="Edge contact points in original sprite coordinates (not relative to bounding box)"
    )
    midpoints_original: Dict[str, Point] = Field(
        default_factory=dict,
        description="Calculated midpoints between edge contacts in original sprite coordinates"
    )
    upper_line_data: LineData = Field(
        default_factory=lambda: LineData(),
        description="Isometric line analysis for the upper portion of the diamond (above the diamond height line)"
    )
    lower_line_data: LineData = Field(
        default_factory=lambda: LineData(),
        description="Isometric line analysis for the lower portion of the diamond (below the diamond height line)"
    )

class DetailedAnalysis(BaseModel):
    """
    Complete geometric analysis of the diamond tile structure.
    
    Provides detailed measurements and analysis for both legacy bounding-box-relative
    coordinates and new original-image-space coordinates. Supports the full two-diamond
    analysis including main diamond and optional upper diamond layers.
    """
    midpoints: Dict[str, Point] = Field(
        default_factory=dict,
        description="Legacy: Calculated midpoints between contact points, relative to bounding box coordinates"
    )
    edge_contact_points: EdgeContactPoints = Field(
        default=EdgeContactPoints(),
        description="Legacy: Edge contact points relative to bounding box coordinates"
    )
    isometric_analysis: IsometricAnalysis = Field(
        default_factory=lambda: IsometricAnalysis(),
        description="Legacy: Isometric line and convex hull analysis relative to bounding box coordinates"
    )
    corner_distances: Dict[str, float] = Field(
        default_factory=dict,
        description="Distances between corner contact points, useful for validating diamond symmetry"
    )
    inter_pixel_distances: Dict[str, float] = Field(
        default_factory=dict,
        description="Distances between key pixel features, used for geometric validation"
    )
    
    # New enhanced data in original image space
    contact_points_data: ContactPointsData = Field(
        default_factory=lambda: ContactPointsData(),
        description="Enhanced analysis data in original sprite coordinates, supporting two-diamond structure analysis"
    )

class SpriteData(BaseModel):
    """
    Complete analysis data for a single diamond tile sprite within the spritesheet.
    
    Represents one isometric diamond tile which can have:
    1. A main diamond structure (defined by diamond_height)
    2. An optional upper diamond layer (defined by frame_upper_z_offset or global upper_z_offset)
    
    The two-diamond system allows modeling complex isometric tiles with elevated sections.
    """
    sprite_index: int = Field(..., description="Index of this sprite within the spritesheet grid (0-based)")
    original_size: Tuple[int, int] = Field(..., description="Original dimensions (width, height) of the sprite in pixels")
    
    # Asset classification for procedural generation pipeline
    asset_type: AssetType = Field(
        default=AssetType.TILE,
        description="Type of isometric asset (tile, wall, door, stair) for procedural generation algorithms"
    )
    
    # Frame-specific settings for diamond structure
    frame_upper_z_offset: int = Field(
        default=0,
        description="Frame-specific upper Z offset in pixels. Creates an upper diamond layer above the main diamond. Overrides global upper_z_offset when > 0."
    )
    manual_diamond_width: Optional[int] = Field(
        default=None,
        description="Manual diamond width override in pixels. When set, overrides bbox.width for diamond calculations. Useful for smaller assets that should align to full tile dimensions."
    )
    
    # Computed properties (optional until calculated)
    pixel_count: Optional[int] = Field(
        default=None,
        description="Number of non-transparent pixels above the alpha threshold"
    )
    bbox: Optional[BoundingBox] = Field(
        default=None,
        description="Tight bounding box around all visible content of the diamond tile"
    )
    diamond_info: Optional[DiamondInfo] = Field(
        default=None,
        description="Geometric measurements of the diamond structure including height calculations"
    )
    detailed_analysis: Optional[DetailedAnalysis] = Field(
        default=None,
        description="Complete geometric analysis including contact points, isometric lines, and convex hulls"
    )
    custom_keypoints: Dict[str, Point] = Field(
        default_factory=dict,
        description="User-defined custom keypoints with arbitrary names for prop attachment, interaction zones, etc."
    )
    
    def get_sprite_rect(self, spritesheet_model: 'SpritesheetModel') -> Tuple[int, int, int, int]:
        """Get the rectangle coordinates for this sprite in the spritesheet"""
        row = self.sprite_index // spritesheet_model.cols
        col = self.sprite_index % spritesheet_model.cols
        x = col * spritesheet_model.sprite_width
        y = row * spritesheet_model.sprite_height
        return (x, y, spritesheet_model.sprite_width, spritesheet_model.sprite_height)
    
    def calculate_savings_percent(self) -> float:
        """Calculate space savings percentage if cropped"""
        if not self.bbox:
            return 0.0
        
        original_area = self.original_size[0] * self.original_size[1]
        if original_area == 0:
            return 0.0
            
        cropped_area = self.bbox.width * self.bbox.height
        return ((original_area - cropped_area) / original_area) * 100
    
    def get_edge_offsets(self) -> Dict[str, int]:
        """Get edge offsets (distances from sprite edges to content)"""
        if not self.bbox:
            return {'top': 0, 'bottom': 0, 'left': 0, 'right': 0}
        
        return {
            'top': self.bbox.y,
            'bottom': self.original_size[1] - (self.bbox.y + self.bbox.height),
            'left': self.bbox.x,
            'right': self.original_size[0] - (self.bbox.x + self.bbox.width)
        }

class SpritesheetModel(BaseModel):
    """
    Complete model for analyzing diamond tile spritesheets.
    
    This model supports the analysis of isometric diamond tiles with a two-diamond structure:
    1. Main Diamond: The primary isometric block defined by natural sprite boundaries
    2. Upper Diamond: An optional elevated section controlled by upper_z_offset
    
    The upper_z_offset creates a horizontal separation line that divides the sprite into
    upper and lower analysis regions, enabling complex multi-layer diamond tile analysis.
    
    Diamond tiles are characterized by:
    - Slanted edges forming a diamond-shaped top surface
    - Vertical flat sides below the diamond
    - Optional upper layer separated by the upper Z line
    - Isometric lines tracing the diagonal edges in 4 directions (NW/NE/SW/SE)
    """
    
    # Core spritesheet properties
    image_path: str = Field(..., description="Path to the source spritesheet image file")
    total_width: int = Field(..., description="Total width of the spritesheet image in pixels")
    total_height: int = Field(..., description="Total height of the spritesheet image in pixels")
    rows: int = Field(..., description="Number of sprite rows in the grid")
    cols: int = Field(..., description="Number of sprite columns in the grid")
    sprite_width: int = Field(..., description="Width of each individual sprite in pixels")
    sprite_height: int = Field(..., description="Height of each individual sprite in pixels")
    
    # Diamond analysis settings
    alpha_threshold: int = Field(
        default=0,
        description="Alpha transparency threshold (0-255). Pixels with alpha > threshold are considered solid content."
    )
    upper_z_offset: int = Field(
        default=0,
        description="Global upper Z offset in pixels from the top of the bounding box. Creates a horizontal line separating upper and lower diamond analysis regions. When > 0, enables two-diamond analysis mode."
    )
    upper_lines_midpoint_mode: bool = Field(
        default=False,
        description="Analysis mode toggle. False: use edge contact points for upper lines. True: use calculated midpoints for upper lines. Midpoint mode is useful when upper_z_offset creates a second diamond layer."
    )
    show_diamond_height: bool = Field(
        default=True,
        description="UI toggle for displaying the diamond height separation line (cyan line)"
    )
    show_overlay: bool = Field(
        default=True,
        description="UI toggle for displaying the analysis overlay with contact points, lines, and hulls"
    )
    show_diamond_vertices: bool = Field(
        default=False,
        description="UI toggle for displaying diamond vertices as white points"
    )
    manual_diamond_width: Optional[int] = Field(
        default=None,
        description="Global manual diamond width override in pixels. When set, overrides bbox.width for diamond calculations across all sprites. Useful for maintaining consistent diamond proportions."
    )
    
    # Computed analysis data
    sprites: List[SpriteData] = Field(
        default_factory=list,
        description="List of analyzed sprite data, one entry per sprite in the grid"
    )
    
    # UI state (excluded from JSON serialization)
    current_sprite_index: int = Field(
        default=0, exclude=True,
        description="Currently selected sprite index for UI display"
    )
    pixeloid_multiplier: int = Field(
        default=1, exclude=True,
        description="Zoom level for pixeloid rendering (1x, 2x, 4x, etc.)"
    )
    pan_x: int = Field(
        default=0, exclude=True,
        description="Horizontal pan offset for UI viewport"
    )
    pan_y: int = Field(
        default=0, exclude=True,
        description="Vertical pan offset for UI viewport"
    )
    
    def initialize_sprites(self):
        """Initialize the sprites list based on grid dimensions"""
        self.sprites = []
        total_sprites = self.rows * self.cols
        
        for i in range(total_sprites):
            sprite_data = SpriteData(
                sprite_index=i,
                original_size=(self.sprite_width, self.sprite_height)
            )
            self.sprites.append(sprite_data)
    
    def get_current_sprite(self) -> Optional[SpriteData]:
        """Get the currently selected sprite data"""
        if 0 <= self.current_sprite_index < len(self.sprites):
            return self.sprites[self.current_sprite_index]
        return None
    
    def get_effective_upper_z_offset(self, sprite_index: int) -> int:
        """Get the effective upper Z offset for a sprite (frame-specific or global)"""
        if 0 <= sprite_index < len(self.sprites):
            sprite = self.sprites[sprite_index]
            # Use frame-specific if set, otherwise use global
            return sprite.frame_upper_z_offset if sprite.frame_upper_z_offset > 0 else self.upper_z_offset
        return self.upper_z_offset
    
    def get_effective_diamond_width(self, sprite_index: int) -> int:
        """Get the effective diamond width for a sprite (frame-specific, global, or bbox width)"""
        if 0 <= sprite_index < len(self.sprites):
            sprite = self.sprites[sprite_index]
            # Priority: frame-specific > global > bbox width
            if sprite.manual_diamond_width and sprite.manual_diamond_width > 0:
                return sprite.manual_diamond_width
            elif self.manual_diamond_width and self.manual_diamond_width > 0:
                return self.manual_diamond_width
            elif sprite.bbox:
                return sprite.bbox.width
            else:
                return 64  # Fallback default
        return 64  # Fallback default
    
    def set_frame_upper_z_offset(self, sprite_index: int, z_offset: int):
        """Set frame-specific upper Z offset for a sprite"""
        if 0 <= sprite_index < len(self.sprites):
            self.sprites[sprite_index].frame_upper_z_offset = max(0, z_offset)
            # Clear analysis data for this sprite
            sprite = self.sprites[sprite_index]
            sprite.pixel_count = None
            sprite.bbox = None
            sprite.diamond_info = None
            sprite.detailed_analysis = None

    def update_analysis_settings(self, alpha_threshold: Optional[int] = None,
                                 upper_z_offset: Optional[int] = None,
                                 upper_lines_midpoint_mode: Optional[bool] = None):
        """Update analysis settings and mark sprites for re-analysis"""
        if alpha_threshold is not None:
            self.alpha_threshold = alpha_threshold
        if upper_z_offset is not None:
            self.upper_z_offset = upper_z_offset
        if upper_lines_midpoint_mode is not None:
            self.upper_lines_midpoint_mode = upper_lines_midpoint_mode
        
        # Clear computed data that depends on these settings
        for sprite in self.sprites:
            sprite.pixel_count = None
            sprite.bbox = None
            sprite.diamond_info = None
            sprite.detailed_analysis = None
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get a summary of analysis results for all sprites"""
        analyzed_count = sum(1 for sprite in self.sprites if sprite.bbox is not None)
        total_savings = 0.0
        avg_savings = 0.0
        
        if analyzed_count > 0:
            savings_list = [sprite.calculate_savings_percent() for sprite in self.sprites if sprite.bbox]
            avg_savings = sum(savings_list) / len(savings_list)
            total_savings = sum(savings_list)
        
        return {
            'total_sprites': len(self.sprites),
            'analyzed_sprites': analyzed_count,
            'average_savings_percent': avg_savings,
            'total_savings_percent': total_savings,
            'alpha_threshold': self.alpha_threshold,
            'upper_z_offset': self.upper_z_offset,
            'upper_lines_midpoint_mode': self.upper_lines_midpoint_mode
        }
    
    def save_to_json(self, path: str):
        """Save the model to a JSON file with clean essential data only"""
        path_obj = Path(path)
        with open(path_obj, 'w') as f:
            # Create clean export data with only essential fields
            data = self._create_clean_export_data()
            json.dump(data, f, indent=2)
    
    def _create_clean_export_data(self) -> Dict[str, Any]:
        """Create clean export data with only essential fields for procedural generation"""
        # Start with core spritesheet properties
        clean_data = {
            'image_path': self.image_path,
            'total_width': self.total_width,
            'total_height': self.total_height,
            'rows': self.rows,
            'cols': self.cols,
            'sprite_width': self.sprite_width,
            'sprite_height': self.sprite_height,
            'alpha_threshold': self.alpha_threshold,
            'upper_z_offset': self.upper_z_offset,
            'upper_lines_midpoint_mode': self.upper_lines_midpoint_mode,
            'show_diamond_height': self.show_diamond_height,
            'show_overlay': self.show_overlay,
            'show_diamond_vertices': self.show_diamond_vertices,
            'sprites': []
        }
        
        # Add clean sprite data (essential fields only)
        for sprite in self.sprites:
            clean_sprite = {
                'sprite_index': sprite.sprite_index,
                'original_size': sprite.original_size,
                'asset_type': sprite.asset_type,
                'frame_upper_z_offset': sprite.frame_upper_z_offset,
            }
            
            # Add essential computed data if available
            if sprite.bbox:
                clean_sprite['bbox'] = {
                    'x': sprite.bbox.x,
                    'y': sprite.bbox.y,
                    'width': sprite.bbox.width,
                    'height': sprite.bbox.height
                }
            
            if sprite.diamond_info:
                clean_sprite['diamond_info'] = self._export_diamond_info(sprite.diamond_info, sprite.sprite_index)
            
            # Always include custom keypoints (empty dict if none)
            clean_sprite['custom_keypoints'] = {
                name: {'x': point.x, 'y': point.y}
                for name, point in sprite.custom_keypoints.items()
            }
            
            clean_data['sprites'].append(clean_sprite)
        
        return clean_data
    
    def _export_diamond_info(self, diamond_info: DiamondInfo, sprite_index: int) -> Dict[str, Any]:
        """Export clean diamond info with vertices and midpoints"""
        exported: Dict[str, Any] = {
            # Legacy measurements for compatibility
            'diamond_height': diamond_info.diamond_height,
            'predicted_flat_height': diamond_info.predicted_flat_height,
            'effective_height': diamond_info.effective_height,
            'line_y': diamond_info.line_y,
            'diamond_width': diamond_info.diamond_width,
            'lower_z_offset': diamond_info.lower_z_offset,
            'upper_z_offset': diamond_info.upper_z_offset,
        }
        
        if diamond_info.upper_z_line_y is not None:
            exported['upper_z_line_y'] = diamond_info.upper_z_line_y
        
        if diamond_info.diamonds_z_offset is not None:
            exported['diamonds_z_offset'] = diamond_info.diamonds_z_offset
        
        # Get the lower diamond's north vertex Y coordinate for z_offset calculation
        lower_vertices = self._get_export_vertex_coords(diamond_info.lower_diamond, sprite_index, 'lower')
        lower_north_y = lower_vertices['north'][1]
        
        # Export lower diamond with vertices and midpoints (z_offset = 0)
        exported['lower_diamond'] = self._export_single_diamond(diamond_info.lower_diamond, sprite_index, 'lower', lower_north_y)
        
        # Export upper diamond if present
        if diamond_info.upper_diamond:
            exported['upper_diamond'] = self._export_single_diamond(diamond_info.upper_diamond, sprite_index, 'upper', lower_north_y)
        
        # Export extra diamonds if present
        if diamond_info.extra_diamonds:
            exported['extra_diamonds'] = {}
            for diamond_name, diamond_data in diamond_info.extra_diamonds.items():
                exported['extra_diamonds'][diamond_name] = self._export_single_diamond(diamond_data, sprite_index, diamond_name, lower_north_y)
        
        return exported
    
    def _export_single_diamond(self, diamond: GameplayDiamondData, sprite_index: int, diamond_level: str, lower_north_y: int) -> Dict[str, Any]:
        """Export a single diamond with all vertices and computed midpoints using correct coordinates and calculated z_offset"""
        # Get the correct vertex coordinates (manual overrides if present, otherwise algorithmic)
        vertices = self._get_export_vertex_coords(diamond, sprite_index, diamond_level)
        
        # Calculate z_offset based on the difference between lower diamond's north vertex Y and this diamond's north vertex Y
        # Lower diamond always has z_offset = 0, other diamonds have z_offset = lower_north_y - this_north_y
        calculated_z_offset = 0.0 if diamond_level == 'lower' else float(lower_north_y - vertices['north'][1])
        
        exported = {
            'north_vertex': {'x': vertices['north'][0], 'y': vertices['north'][1]},
            'south_vertex': {'x': vertices['south'][0], 'y': vertices['south'][1]},
            'east_vertex': {'x': vertices['east'][0], 'y': vertices['east'][1]},
            'west_vertex': {'x': vertices['west'][0], 'y': vertices['west'][1]},
            'center': {'x': diamond.center.x, 'y': diamond.center.y},
            'z_offset': calculated_z_offset
        }
        
        # Compute midpoints using the correct vertex coordinates
        exported['north_east_midpoint'] = {
            'x': (vertices['north'][0] + vertices['east'][0]) // 2,
            'y': (vertices['north'][1] + vertices['east'][1]) // 2
        }
        exported['east_south_midpoint'] = {
            'x': (vertices['east'][0] + vertices['south'][0]) // 2,
            'y': (vertices['east'][1] + vertices['south'][1]) // 2
        }
        exported['south_west_midpoint'] = {
            'x': (vertices['south'][0] + vertices['west'][0]) // 2,
            'y': (vertices['south'][1] + vertices['west'][1]) // 2
        }
        exported['west_north_midpoint'] = {
            'x': (vertices['west'][0] + vertices['north'][0]) // 2,
            'y': (vertices['west'][1] + vertices['north'][1]) // 2
        }
        
        # Export sub-diamonds if present
        if diamond.sub_diamonds:
            exported['sub_diamonds'] = {}
            for quadrant, sub_diamond in diamond.sub_diamonds.items():
                sub_exported = {
                    'quadrant': sub_diamond.quadrant,
                    'north_vertex': {'x': sub_diamond.north_vertex.x, 'y': sub_diamond.north_vertex.y},
                    'south_vertex': {'x': sub_diamond.south_vertex.x, 'y': sub_diamond.south_vertex.y},
                    'east_vertex': {'x': sub_diamond.east_vertex.x, 'y': sub_diamond.east_vertex.y},
                    'west_vertex': {'x': sub_diamond.west_vertex.x, 'y': sub_diamond.west_vertex.y},
                    'center': {'x': sub_diamond.center.x, 'y': sub_diamond.center.y},
                    'is_walkable': sub_diamond.is_walkable
                }
                
                # Export edge properties for this sub-diamond (always include, even if default)
                edge_props = {}
                for edge_name in ['north_west', 'north_east', 'south_west', 'south_east']:
                    edge_attr = f"{edge_name}_edge"
                    if hasattr(sub_diamond, edge_attr):
                        edge = getattr(sub_diamond, edge_attr)
                        edge_props[edge_name] = {
                            'blocks_line_of_sight': edge.blocks_line_of_sight,
                            'blocks_movement': edge.blocks_movement
                        }
                
                # Always include edge properties structure
                sub_exported['edge_properties'] = edge_props
                
                exported['sub_diamonds'][quadrant] = sub_exported
        
        return exported
    
    def _get_export_vertex_coords(self, diamond: GameplayDiamondData, sprite_index: int, diamond_level: str) -> Dict[str, Tuple[int, int]]:
        """Get vertex coordinates for export, using manual overrides if present"""
        # Access the renderer's manual vertices if available
        manual_vertices = getattr(self, '_renderer_manual_vertices', {})
        manual_overrides = manual_vertices.get(sprite_index, {}).get(diamond_level, {})
        
        # Map vertex names to coordinates
        vertices = {}
        vertex_data = [
            ('north', diamond.north_vertex),
            ('south', diamond.south_vertex),
            ('east', diamond.east_vertex),
            ('west', diamond.west_vertex)
        ]
        
        for vertex_name, vertex_point in vertex_data:
            # Use manual override if present, otherwise use algorithmic
            if vertex_name in manual_overrides:
                vertices[vertex_name] = manual_overrides[vertex_name]
            else:
                vertices[vertex_name] = (vertex_point.x, vertex_point.y)
        
        return vertices
    
    def _compress_line_data_for_json(self, data: Dict[str, Any]):
        """Compress line data to compact format for JSON serialization"""
        if 'sprites' not in data:
            return
            
        for sprite_data in data['sprites']:
            if 'detailed_analysis' not in sprite_data or not sprite_data['detailed_analysis']:
                continue
                
            detailed = sprite_data['detailed_analysis']
            
            # Compress IsometricAnalysis lines
            if 'isometric_analysis' in detailed and detailed['isometric_analysis']:
                iso_analysis = detailed['isometric_analysis']
                
                # Compress main lines to line_segments
                if 'lines' in iso_analysis and iso_analysis['lines']:
                    line_segments = {}
                    for direction, points in iso_analysis['lines'].items():
                        if points and len(points) >= 2:
                            line_segments[direction] = [points[0], points[-1]]  # start, end
                    iso_analysis['line_segments'] = line_segments
                    del iso_analysis['lines']  # Remove full lines from JSON
                
                # Compress convex hulls to hull_bounds
                if 'convex_hulls' in iso_analysis and iso_analysis['convex_hulls']:
                    hull_bounds = {}
                    for direction, hull_points in iso_analysis['convex_hulls'].items():
                        if hull_points:
                            min_x = min(p['x'] for p in hull_points)
                            max_x = max(p['x'] for p in hull_points)
                            min_y = min(p['y'] for p in hull_points)
                            max_y = max(p['y'] for p in hull_points)
                            hull_bounds[direction] = [
                                {'x': min_x, 'y': min_y},
                                {'x': max_x, 'y': max_y}
                            ]
                    iso_analysis['hull_bounds'] = hull_bounds
                    del iso_analysis['convex_hulls']  # Remove full hulls from JSON
                
                # Remove legacy fields
                if 'line_points' in iso_analysis:
                    del iso_analysis['line_points']
                if 'convex_hull_area' in iso_analysis:
                    del iso_analysis['convex_hull_area']
            
            # Compress ContactPointsData lines
            if 'contact_points_data' in detailed and detailed['contact_points_data']:
                contact_data = detailed['contact_points_data']
                
                # Compress upper_line_data
                if 'upper_line_data' in contact_data:
                    self._compress_line_data_dict(contact_data['upper_line_data'])
                
                # Compress lower_line_data
                if 'lower_line_data' in contact_data:
                    self._compress_line_data_dict(contact_data['lower_line_data'])
    
    def _compress_line_data_dict(self, line_data: Dict[str, Any]):
        """Compress a LineData dictionary"""
        # Compress contact_points_mode
        if 'contact_points_mode' in line_data and line_data['contact_points_mode']:
            segments = {}
            for direction, points in line_data['contact_points_mode'].items():
                if points and len(points) >= 2:
                    segments[direction] = [points[0], points[-1]]
            line_data['contact_points_segments'] = segments
            del line_data['contact_points_mode']
        
        # Compress midpoint_mode
        if 'midpoint_mode' in line_data and line_data['midpoint_mode']:
            segments = {}
            for direction, points in line_data['midpoint_mode'].items():
                if points and len(points) >= 2:
                    segments[direction] = [points[0], points[-1]]
            line_data['midpoint_segments'] = segments
            del line_data['midpoint_mode']
    
    def _convert_numpy_types(self, obj):
        """Recursively convert numpy types to Python types for JSON serialization"""
        import numpy as np
        
        if isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
    
    @classmethod
    def load_from_json(cls, path: str) -> 'SpritesheetModel':
        """Load the model from a JSON file (new clean format only)"""
        path_obj = Path(path)
        with open(path_obj, 'r') as f:
            data = json.load(f)
        
        # Create model from the clean data
        model = cls._load_from_clean_format(data)
        return model
    
    @classmethod
    def _load_from_clean_format(cls, data: Dict[str, Any]) -> 'SpritesheetModel':
        """Load from the new clean JSON format"""
        # Create model with core properties
        model_data = {
            'image_path': data['image_path'],
            'total_width': data['total_width'],
            'total_height': data['total_height'],
            'rows': data['rows'],
            'cols': data['cols'],
            'sprite_width': data['sprite_width'],
            'sprite_height': data['sprite_height'],
            'alpha_threshold': data.get('alpha_threshold', 0),
            'upper_z_offset': data.get('upper_z_offset', 0),
            'upper_lines_midpoint_mode': data.get('upper_lines_midpoint_mode', False),
            'show_diamond_height': data.get('show_diamond_height', True),
            'show_overlay': data.get('show_overlay', True),
            'show_diamond_vertices': data.get('show_diamond_vertices', False),
            'sprites': []
        }
        
        # Process sprite data
        for sprite_data in data.get('sprites', []):
            sprite = SpriteData(
                sprite_index=sprite_data['sprite_index'],
                original_size=tuple(sprite_data['original_size']),
                asset_type=sprite_data.get('asset_type', AssetType.TILE),
                frame_upper_z_offset=sprite_data.get('frame_upper_z_offset', 0)
            )
            
            # Restore bbox if present
            if 'bbox' in sprite_data:
                bbox_data = sprite_data['bbox']
                sprite.bbox = BoundingBox(
                    x=bbox_data['x'],
                    y=bbox_data['y'],
                    width=bbox_data['width'],
                    height=bbox_data['height']
                )
            
            # Restore diamond_info if present
            if 'diamond_info' in sprite_data:
                sprite.diamond_info = cls._import_diamond_info(sprite_data['diamond_info'])
            
            # Restore custom keypoints if present
            if 'custom_keypoints' in sprite_data:
                sprite.custom_keypoints = {
                    name: Point(x=point_data['x'], y=point_data['y'])
                    for name, point_data in sprite_data['custom_keypoints'].items()
                }
            
            model_data['sprites'].append(sprite)
        
        model = cls(**model_data)
        return model
    
    def transfer_vertices_to_manual(self, renderer):
        """Transfer all diamond vertices from model to renderer as manual vertices"""
        for sprite in self.sprites:
            if sprite.diamond_info:
                sprite_key = sprite.sprite_index
                
                # Initialize renderer manual vertices for this sprite if not exists
                if sprite_key not in renderer.manual_vertices:
                    renderer.manual_vertices[sprite_key] = {}
                
                # Transfer lower diamond vertices
                if sprite.diamond_info.lower_diamond:
                    lower = sprite.diamond_info.lower_diamond
                    renderer.manual_vertices[sprite_key]['lower'] = {
                        'north': (lower.north_vertex.x, lower.north_vertex.y),
                        'south': (lower.south_vertex.x, lower.south_vertex.y),
                        'east': (lower.east_vertex.x, lower.east_vertex.y),
                        'west': (lower.west_vertex.x, lower.west_vertex.y)
                    }
                
                # Transfer upper diamond vertices if present
                if sprite.diamond_info.upper_diamond:
                    upper = sprite.diamond_info.upper_diamond
                    renderer.manual_vertices[sprite_key]['upper'] = {
                        'north': (upper.north_vertex.x, upper.north_vertex.y),
                        'south': (upper.south_vertex.x, upper.south_vertex.y),
                        'east': (upper.east_vertex.x, upper.east_vertex.y),
                        'west': (upper.west_vertex.x, upper.west_vertex.y)
                    }
                
                # Transfer custom diamond vertices if present
                for diamond_name, custom_diamond in sprite.diamond_info.extra_diamonds.items():
                    renderer.manual_vertices[sprite_key][diamond_name] = {
                        'north': (custom_diamond.north_vertex.x, custom_diamond.north_vertex.y),
                        'south': (custom_diamond.south_vertex.x, custom_diamond.south_vertex.y),
                        'east': (custom_diamond.east_vertex.x, custom_diamond.east_vertex.y),
                        'west': (custom_diamond.west_vertex.x, custom_diamond.west_vertex.y)
                    }
    
    @classmethod
    def _import_diamond_info(cls, diamond_data: Dict[str, Any]) -> DiamondInfo:
        """Import diamond info from clean JSON format"""
        # Import lower diamond
        lower_diamond = cls._import_single_diamond(diamond_data['lower_diamond'])
        
        # Import upper diamond if present
        upper_diamond = None
        if 'upper_diamond' in diamond_data:
            upper_diamond = cls._import_single_diamond(diamond_data['upper_diamond'])
        
        # Import extra diamonds if present
        extra_diamonds = {}
        if 'extra_diamonds' in diamond_data:
            for diamond_name, extra_diamond_data in diamond_data['extra_diamonds'].items():
                extra_diamonds[diamond_name] = cls._import_single_diamond(extra_diamond_data)
        
        return DiamondInfo(
            diamond_height=diamond_data['diamond_height'],
            predicted_flat_height=diamond_data['predicted_flat_height'],
            effective_height=diamond_data['effective_height'],
            line_y=diamond_data['line_y'],
            upper_z_line_y=diamond_data.get('upper_z_line_y'),
            lower_diamond=lower_diamond,
            upper_diamond=upper_diamond,
            extra_diamonds=extra_diamonds,
            diamond_width=diamond_data['diamond_width'],
            lower_z_offset=diamond_data['lower_z_offset'],
            upper_z_offset=diamond_data['upper_z_offset'],
            diamonds_z_offset=diamond_data.get('diamonds_z_offset')
        )
    
    @classmethod
    def _import_single_diamond(cls, diamond_data: Dict[str, Any]) -> GameplayDiamondData:
        """Import a single diamond from clean JSON format"""
        # Create basic GameplayDiamondData
        gameplay_diamond = GameplayDiamondData(
            north_vertex=Point(x=diamond_data['north_vertex']['x'], y=diamond_data['north_vertex']['y']),
            south_vertex=Point(x=diamond_data['south_vertex']['x'], y=diamond_data['south_vertex']['y']),
            east_vertex=Point(x=diamond_data['east_vertex']['x'], y=diamond_data['east_vertex']['y']),
            west_vertex=Point(x=diamond_data['west_vertex']['x'], y=diamond_data['west_vertex']['y']),
            center=Point(x=diamond_data['center']['x'], y=diamond_data['center']['y']),
            z_offset=diamond_data['z_offset'],
            # Import midpoints if present
            north_east_midpoint=Point(x=diamond_data['north_east_midpoint']['x'], y=diamond_data['north_east_midpoint']['y']) if 'north_east_midpoint' in diamond_data else None,
            east_south_midpoint=Point(x=diamond_data['east_south_midpoint']['x'], y=diamond_data['east_south_midpoint']['y']) if 'east_south_midpoint' in diamond_data else None,
            south_west_midpoint=Point(x=diamond_data['south_west_midpoint']['x'], y=diamond_data['south_west_midpoint']['y']) if 'south_west_midpoint' in diamond_data else None,
            west_north_midpoint=Point(x=diamond_data['west_north_midpoint']['x'], y=diamond_data['west_north_midpoint']['y']) if 'west_north_midpoint' in diamond_data else None
        )
        
        # Import sub-diamonds if present
        if 'sub_diamonds' in diamond_data and diamond_data['sub_diamonds']:
            gameplay_diamond.sub_diamonds = {}
            for quadrant, sub_data in diamond_data['sub_diamonds'].items():
                # Handle both old format (main_vertex/midpoint_a/midpoint_b) and new format (4 vertices)
                if 'north_vertex' in sub_data:
                    # New format with proper 4 vertices
                    sub_diamond = SubDiamondData(
                        quadrant=sub_data['quadrant'],
                        north_vertex=Point(x=sub_data['north_vertex']['x'], y=sub_data['north_vertex']['y']),
                        south_vertex=Point(x=sub_data['south_vertex']['x'], y=sub_data['south_vertex']['y']),
                        east_vertex=Point(x=sub_data['east_vertex']['x'], y=sub_data['east_vertex']['y']),
                        west_vertex=Point(x=sub_data['west_vertex']['x'], y=sub_data['west_vertex']['y']),
                        center=Point(x=sub_data['center']['x'], y=sub_data['center']['y']),
                        is_walkable=sub_data.get('is_walkable')
                    )
                    
                    # Import edge properties for this sub-diamond if present
                    if 'edge_properties' in sub_data:
                        for edge_name, edge_data in sub_data['edge_properties'].items():
                            edge_attr = f"{edge_name}_edge"
                            if hasattr(sub_diamond, edge_attr):
                                edge_props = EdgeProperties(
                                    blocks_line_of_sight=edge_data.get('blocks_line_of_sight'),
                                    blocks_movement=edge_data.get('blocks_movement')
                                )
                                setattr(sub_diamond, edge_attr, edge_props)
                    
                    gameplay_diamond.sub_diamonds[quadrant] = sub_diamond
                else:
                    # Old format - convert triangular to diamond shape (no edge properties to import)
                    main_vertex = Point(x=sub_data['main_vertex']['x'], y=sub_data['main_vertex']['y'])
                    midpoint_a = Point(x=sub_data['midpoint_a']['x'], y=sub_data['midpoint_a']['y'])
                    midpoint_b = Point(x=sub_data['midpoint_b']['x'], y=sub_data['midpoint_b']['y'])
                    center = Point(x=sub_data['center']['x'], y=sub_data['center']['y'])
                    
                    # Convert to diamond format based on quadrant
                    if quadrant == 'north':
                        gameplay_diamond.sub_diamonds[quadrant] = SubDiamondData(
                            quadrant=quadrant,
                            north_vertex=main_vertex,
                            south_vertex=center,
                            east_vertex=midpoint_b,
                            west_vertex=midpoint_a,
                            center=Point(x=(main_vertex.x + center.x) // 2, y=(main_vertex.y + center.y) // 2),
                            is_walkable=sub_data.get('is_walkable')
                        )
                    elif quadrant == 'south':
                        gameplay_diamond.sub_diamonds[quadrant] = SubDiamondData(
                            quadrant=quadrant,
                            north_vertex=center,
                            south_vertex=main_vertex,
                            east_vertex=midpoint_b,
                            west_vertex=midpoint_a,
                            center=Point(x=(main_vertex.x + center.x) // 2, y=(main_vertex.y + center.y) // 2),
                            is_walkable=sub_data.get('is_walkable')
                        )
                    elif quadrant == 'east':
                        gameplay_diamond.sub_diamonds[quadrant] = SubDiamondData(
                            quadrant=quadrant,
                            north_vertex=midpoint_a,
                            south_vertex=midpoint_b,
                            east_vertex=main_vertex,
                            west_vertex=center,
                            center=Point(x=(main_vertex.x + center.x) // 2, y=(main_vertex.y + center.y) // 2),
                            is_walkable=sub_data.get('is_walkable')
                        )
                    elif quadrant == 'west':
                        gameplay_diamond.sub_diamonds[quadrant] = SubDiamondData(
                            quadrant=quadrant,
                            north_vertex=midpoint_a,
                            south_vertex=midpoint_b,
                            east_vertex=center,
                            west_vertex=main_vertex,
                            center=Point(x=(main_vertex.x + center.x) // 2, y=(main_vertex.y + center.y) // 2),
                            is_walkable=sub_data.get('is_walkable')
                        )
        
        return gameplay_diamond
    
    def set_manual_vertices_for_export(self, manual_vertices: Dict[int, Dict[str, Dict[str, Tuple[int, int]]]]):
        """Set manual vertices data from renderer for export"""
        self._renderer_manual_vertices = manual_vertices
    
    @classmethod
    def _restore_line_data_from_json(cls, data: Dict[str, Any]):
        """Restore full line data from compact format after JSON loading"""
        if 'sprites' not in data:
            return
            
        for sprite_data in data['sprites']:
            if 'detailed_analysis' not in sprite_data or not sprite_data['detailed_analysis']:
                continue
                
            detailed = sprite_data['detailed_analysis']
            
            # Restore IsometricAnalysis lines
            if 'isometric_analysis' in detailed and detailed['isometric_analysis']:
                iso_analysis = detailed['isometric_analysis']
                
                # Restore lines from line_segments (simplified - just start/end for now)
                if 'line_segments' in iso_analysis:
                    lines = {}
                    for direction, segment in iso_analysis['line_segments'].items():
                        if len(segment) == 2:
                            # For now, just use start and end points
                            # In a real implementation, you'd regenerate the full line
                            lines[direction] = [
                                {'x': segment[0]['x'], 'y': segment[0]['y']},
                                {'x': segment[1]['x'], 'y': segment[1]['y']}
                            ]
                    iso_analysis['lines'] = lines
                    del iso_analysis['line_segments']
                
                # Restore convex_hulls from hull_bounds (simplified)
                if 'hull_bounds' in iso_analysis:
                    convex_hulls = {}
                    for direction, bounds in iso_analysis['hull_bounds'].items():
                        if len(bounds) == 2:
                            # Generate a simple rectangle for the hull
                            min_point, max_point = bounds
                            hull_points = [
                                {'x': min_point['x'], 'y': min_point['y']},
                                {'x': max_point['x'], 'y': min_point['y']},
                                {'x': max_point['x'], 'y': max_point['y']},
                                {'x': min_point['x'], 'y': max_point['y']}
                            ]
                            convex_hulls[direction] = hull_points
                    iso_analysis['convex_hulls'] = convex_hulls
                    del iso_analysis['hull_bounds']
                
                # Restore legacy fields
                iso_analysis['line_points'] = []
                iso_analysis['convex_hull_area'] = []
            
            # Restore ContactPointsData lines
            if 'contact_points_data' in detailed and detailed['contact_points_data']:
                contact_data = detailed['contact_points_data']
                
                # Restore upper_line_data
                if 'upper_line_data' in contact_data:
                    cls._restore_line_data_dict(contact_data['upper_line_data'])
                
                # Restore lower_line_data
                if 'lower_line_data' in contact_data:
                    cls._restore_line_data_dict(contact_data['lower_line_data'])
    
    @classmethod
    def _restore_line_data_dict(cls, line_data: Dict[str, Any]):
        """Restore a LineData dictionary from compact format"""
        # Restore contact_points_mode
        if 'contact_points_segments' in line_data:
            contact_points_mode = {}
            for direction, segment in line_data['contact_points_segments'].items():
                if len(segment) == 2:
                    contact_points_mode[direction] = [
                        {'x': segment[0]['x'], 'y': segment[0]['y']},
                        {'x': segment[1]['x'], 'y': segment[1]['y']}
                    ]
            line_data['contact_points_mode'] = contact_points_mode
            del line_data['contact_points_segments']
        else:
            line_data['contact_points_mode'] = {}
        
        # Restore midpoint_mode
        if 'midpoint_segments' in line_data:
            midpoint_mode = {}
            for direction, segment in line_data['midpoint_segments'].items():
                if len(segment) == 2:
                    midpoint_mode[direction] = [
                        {'x': segment[0]['x'], 'y': segment[0]['y']},
                        {'x': segment[1]['x'], 'y': segment[1]['y']}
                    ]
            line_data['midpoint_mode'] = midpoint_mode
            del line_data['midpoint_segments']
        else:
            line_data['midpoint_mode'] = {}
    
    @classmethod
    def create_from_image(cls, image_path: str, rows: int, cols: int, 
                         total_width: int, total_height: int) -> 'SpritesheetModel':
        """Create a new model from an image file"""
        sprite_width = total_width // cols
        sprite_height = total_height // rows
        
        model = cls(
            image_path=image_path,
            total_width=total_width,
            total_height=total_height,
            rows=rows,
            cols=cols,
            sprite_width=sprite_width,
            sprite_height=sprite_height
        )
        
        model.initialize_sprites()
        return model
    
    def model_dump_json_compatible(self) -> Dict[str, Any]:
        """Get a JSON-compatible dictionary representation"""
        return self.model_dump(exclude={'current_sprite_index', 'pixeloid_multiplier', 'pan_x', 'pan_y'})

# Helper functions for converting between different formats

def point_from_tuple(point_tuple: Optional[Tuple[int, int]]) -> Optional[Point]:
    """Convert a tuple to a Point object"""
    if point_tuple is None:
        return None
    return Point(x=point_tuple[0], y=point_tuple[1])

def point_to_tuple(point: Optional[Point]) -> Optional[Tuple[int, int]]:
    """Convert a Point object to a tuple"""
    if point is None:
        return None
    return (point.x, point.y)

def bbox_from_pygame_rect(rect) -> Optional[BoundingBox]:
    """Convert a pygame.Rect to a BoundingBox object"""
    if rect is None:
        return None
    return BoundingBox(x=rect.x, y=rect.y, width=rect.width, height=rect.height)

def points_from_list(points_list: List[Tuple[int, int]]) -> List[Point]:
    """Convert a list of tuples to a list of Point objects"""
    return [Point(x=x, y=y) for x, y in points_list]

def points_to_list(points: List[Point]) -> List[Tuple[int, int]]:
    """Convert a list of Point objects to a list of tuples"""
    return [(point.x, point.y) for point in points]