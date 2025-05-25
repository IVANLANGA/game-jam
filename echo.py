import pygame
from collections import deque
from settings import TILE_SIZE, WHITE, BLACK, RED, YELLOW, GOOD_ECHO_LAG_FRAMES

class EnemySpriteManager:
    def __init__(self):
        self.sprite_sheet = pygame.image.load("assets/img/enemy.png").convert_alpha()
        self.frame_width = 32
        self.frame_height = 32
        self.frames_per_row = 10
        self.directions = ["down", "up", "right", "left"]
        self.row_map = {
            "down": 0,
            "up": 32,
            "right": 64,
            "left": 96,
        }
        self.animations = {}
        scale = 2 
        for dir_name in self.directions:
            y = self.row_map[dir_name]
            frames = []
            for i in range(self.frames_per_row):
                rect = pygame.Rect(i * self.frame_width, y, self.frame_width, self.frame_height)
                frame = self.sprite_sheet.subsurface(rect)
                frame = pygame.transform.scale(frame, (self.frame_width * scale, self.frame_height * scale))
                frames.append(frame)
            self.animations[dir_name] = frames

    def get_frame(self, direction, frame_idx):
        return self.animations[direction][frame_idx % self.frames_per_row]

# --- Friend (Good Echo) Sprite Manager ---
class FriendSpriteManager:
    def __init__(self):
        self.sprite_sheet = pygame.image.load("assets/img/friend.png").convert_alpha()
        self.frame_width = 64
        self.frame_height = 64
        self.frames_per_row = 8  
        self.directions = ["down", "left", "right", "up"]
        self.row_map = {
            "down": 0,
            "left": 64,
            "right": 128,
            "up": 192,
        }
        self.animations = {}
        sheet_width, sheet_height = self.sprite_sheet.get_size()
        scale = 2  
        for dir_name in self.directions:
            y = self.row_map[dir_name]
            frames = []
            for i in range(self.frames_per_row):
                rect = pygame.Rect(i * self.frame_width, y, self.frame_width, self.frame_height)
                # Only add frame if within bounds
                if rect.right <= sheet_width and rect.bottom <= sheet_height:
                    frame = self.sprite_sheet.subsurface(rect)
                    frame = pygame.transform.scale(frame, (self.frame_width * scale, self.frame_height * scale))
                    frames.append(frame)
            self.animations[dir_name] = frames

    def get_frame(self, direction, frame_idx):
        return self.animations[direction][frame_idx % self.frames_per_row]

def get_direction_from_path(path, idx):
    # Returns "down", "up", "right", or "left" based on movement vector
    if len(path) < 2:
        return "down"
    if idx == 0:
        prev = path[0]
        curr = path[1] if len(path) > 1 else path[0]
    else:
        prev = path[idx - 1]
        curr = path[idx]
    dx = curr.x - prev.x
    dy = curr.y - prev.y
    if abs(dx) > abs(dy):
        return "right" if dx > 0 else "left"
    else:
        return "down" if dy > 0 else "up"

def get_direction_from_vector(vec):
    dx, dy = vec.x, vec.y
    if abs(dx) > abs(dy):
        return "right" if dx > 0 else "left"
    else:
        return "down" if dy > 0 else "up"

class EchoManager:
    def __init__(self):
        self.echoes = []
        self.echo_frames = []
        self.recording = []

        self.echo_buffers = []

        self.good_echo_active = False
        self.good_echo_pos = None
        self.good_echo_timer = 0
        self.good_echo_current_duration = None
        self.good_echo_target_idx = None  # Index of the echo being hunted
        self.good_echo_speed = 3  # Pixels per frame, adjust as needed

        self.freeze_bad_echoes = False
        self.freeze_timer = 0

        # --- Enemy sprite animation ---
        self.enemy_sprites = EnemySpriteManager()
        self.enemy_anim_timer = 0
        self.enemy_anim_delay = 6  # Adjust for animation speed
        self.enemy_anim_frame = 0

        # --- Friend sprite animation ---
        self.friend_sprites = FriendSpriteManager()
        self.friend_anim_timer = 0
        self.friend_anim_delay = 6
        self.friend_anim_frame = 0
        self.friend_last_direction = "down"

        self.sounds = None  # Will be set from main

    def set_sounds(self, sounds):
        self.sounds = sounds

    def start_good_echo(self, duration_base, duration_increment):
        self.good_echo_active = True
        if self.good_echo_current_duration is None:
            self.good_echo_current_duration = duration_base
        self.good_echo_timer = self.good_echo_current_duration
        self.good_echo_current_duration += duration_increment
        self.good_echo_pos = None  # Will be set in update
        self.good_echo_target_idx = None

    def freeze_bad(self, duration_frames):
        self.freeze_bad_echoes = True
        self.freeze_timer = duration_frames

    def update(self, player_pos, screen):
        # Append player pos to recording
        self.recording.append(player_pos.copy())

        # Good echo hunting logic
        friend_direction_vec = pygame.Vector2(0, 1)  # Default down
        if self.good_echo_active:
            if self.good_echo_pos is None:
                self.good_echo_pos = player_pos.copy()
            # Find nearest bad echo to hunt
            if self.echoes:
                min_dist = float('inf')
                target_idx = None
                target_pos = None
                for i, path in enumerate(self.echoes):
                    if len(path) > 0:
                        idx = self.echo_frames[i] % len(path)
                        echo_pos = path[idx]
                        dist = self.good_echo_pos.distance_to(echo_pos)
                        if dist < min_dist:
                            min_dist = dist
                            target_idx = i
                            target_pos = echo_pos
                self.good_echo_target_idx = target_idx
                # Move good echo towards target
                if target_pos is not None:
                    direction = (target_pos - self.good_echo_pos)
                    if direction.length() > 0:
                        friend_direction_vec = direction
                        direction = direction.normalize()
                        self.good_echo_pos += direction * self.good_echo_speed
                    # Check collision with target echo
                    good_echo_rect = pygame.Rect(self.good_echo_pos.x, self.good_echo_pos.y, TILE_SIZE, TILE_SIZE)
                    echo_rect = pygame.Rect(target_pos.x, target_pos.y, TILE_SIZE, TILE_SIZE)
                    if good_echo_rect.colliderect(echo_rect):
                        # Play attack sound if available
                        if self.sounds and "attack" in self.sounds:
                            self.sounds["attack"].play()
                        del self.echoes[target_idx]
                        del self.echo_frames[target_idx]
                        self.good_echo_target_idx = None
            else:
                self.good_echo_target_idx = None
        else:
            self.good_echo_pos = None
            self.good_echo_target_idx = None

        # Handle freeze timer
        if self.freeze_bad_echoes:
            self.freeze_timer -= 1
            if self.freeze_timer <= 0:
                self.freeze_bad_echoes = False

        # Echo buffer flashing before spawning actual echo
        new_buffers = []
        for buffer in self.echo_buffers:
            buffer['color_timer'] -= 1
            if buffer['color_timer'] <= 0:
                buffer['color_state'] = not buffer['color_state']
                buffer['color_timer'] = 15

            flash_color = WHITE if buffer['color_state'] else BLACK
            pygame.draw.rect(screen, flash_color, (*buffer['pos'], TILE_SIZE, TILE_SIZE))

            buffer['timer'] -= 1
            if buffer['timer'] <= 0:
                self.echoes.append(buffer['path'])
                self.echo_frames.append(0)
            else:
                new_buffers.append(buffer)
        self.echo_buffers = new_buffers

        # --- Animate enemy (bad echo) frames ---
        if not self.freeze_bad_echoes:
            self.enemy_anim_timer += 1
            if self.enemy_anim_timer >= self.enemy_anim_delay:
                self.enemy_anim_timer = 0
                self.enemy_anim_frame = (self.enemy_anim_frame + 1) % self.enemy_sprites.frames_per_row

        # --- Animate friend (good echo) frames ---
        self.friend_anim_timer += 1
        if self.friend_anim_timer >= self.friend_anim_delay:
            self.friend_anim_timer = 0
            self.friend_anim_frame = (self.friend_anim_frame + 1) % self.friend_sprites.frames_per_row

        # Update and draw echoes
        surviving_echoes = []
        surviving_frames = []
        for i in range(len(self.echoes)):
            path = self.echoes[i]
            if len(path) > 0:
                index = self.echo_frames[i] % len(path)
                echo_pos = path[index]

                # --- Animated enemy sprite instead of rectangle ---
                direction = get_direction_from_path(path, index)
                frame_idx = self.enemy_anim_frame
                frame = self.enemy_sprites.get_frame(direction, frame_idx)
                # Center the 4x sprite on the echo position (TILE_SIZE square)
                sprite_rect = frame.get_rect()
                sprite_rect.center = (echo_pos.x + TILE_SIZE // 2, echo_pos.y + TILE_SIZE // 2)
                screen.blit(frame, sprite_rect)

                # Only advance frame if not frozen
                if not self.freeze_bad_echoes:
                    surviving_echoes.append(path)
                    surviving_frames.append(self.echo_frames[i] + 1)
                else:
                    surviving_echoes.append(path)
                    surviving_frames.append(self.echo_frames[i])
        self.echoes = surviving_echoes
        self.echo_frames = surviving_frames

        # Good echo timer update
        if self.good_echo_active:
            self.good_echo_timer -= 1
            if self.good_echo_timer <= 0:
                self.good_echo_active = False
                self.good_echo_pos = None
                self.good_echo_target_idx = None

        # Draw good echo as animated sprite
        if self.good_echo_active and self.good_echo_pos:
            direction = get_direction_from_vector(friend_direction_vec)
            self.friend_last_direction = direction
            frame = self.friend_sprites.get_frame(direction, self.friend_anim_frame)
            sprite_rect = frame.get_rect()
            sprite_rect.center = (self.good_echo_pos.x + TILE_SIZE // 2, self.good_echo_pos.y + TILE_SIZE // 2)
            screen.blit(frame, sprite_rect)

    def add_echo_buffer(self, loop_path, pos):
        self.echo_buffers.append({
            'path': loop_path,
            'timer': 120,  # Could pass as param or use constant
            'color_state': True,
            'color_timer': 15,
            'pos': pos
        })

    def check_collision(self, player_pos):
        player_rect = pygame.Rect(player_pos.x, player_pos.y, TILE_SIZE, TILE_SIZE)
        for i, path in enumerate(self.echoes):
            index = self.echo_frames[i] % len(path)
            echo_pos = path[index]
            echo_rect = pygame.Rect(echo_pos.x, echo_pos.y, TILE_SIZE, TILE_SIZE)
            if player_rect.colliderect(echo_rect):
                return i + 1  # round number or echo index
        return None
