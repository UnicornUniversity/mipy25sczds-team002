import pygame
import random


class MuzzleFlash:
    """Simple muzzle flash effect"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lifetime = 0.1  # Very short flash
        self.age = 0

    def update(self, dt):
        self.age += dt
        return self.age < self.lifetime

    def render(self, screen, camera_offset):
        if self.age < self.lifetime:
            # Simple yellow circle for muzzle flash
            screen_x = int(self.x - camera_offset[0])
            screen_y = int(self.y - camera_offset[1])
            radius = int(8 * (1 - self.age / self.lifetime))  # Shrinking
            if radius > 0:
                pygame.draw.circle(screen, (255, 255, 0), (screen_x, screen_y), radius)


class BulletImpact:
    """Simple bullet impact effect"""
    def __init__(self, x, y, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = 0.2
        self.age = 0

    def update(self, dt):
        self.age += dt
        return self.age < self.lifetime

    def render(self, screen, camera_offset):
        if self.age < self.lifetime:
            # Simple spark effect
            screen_x = int(self.x - camera_offset[0])
            screen_y = int(self.y - camera_offset[1])
            alpha = int(255 * (1 - self.age / self.lifetime))
            color_with_alpha = (*self.color, alpha)

            # Draw small cross for impact
            pygame.draw.line(screen, self.color, (screen_x-3, screen_y), (screen_x+3, screen_y), 2)
            pygame.draw.line(screen, self.color, (screen_x, screen_y-3), (screen_x, screen_y+3), 2)


class BloodSplatter:
    """Enhanced blood splatter effect with multiple particles"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lifetime = 0.8  # Longer lifetime for more dramatic effect
        self.age = 0

        # Create multiple blood particles for a less dramatic effect
        self.particles = []
        num_particles = random.randint(3, 6)  # Fewer particles

        for _ in range(num_particles):
            # Random offset from center (smaller area)
            offset_x = random.randint(-8, 8)
            offset_y = random.randint(-8, 8)

            # Random size (smaller)
            size = random.randint(1, 4)

            # Random lifetime offset
            lifetime_offset = random.uniform(-0.1, 0.1)

            # Random color variation (darker to brighter red)
            red = random.randint(120, 180)

            self.particles.append({
                'x': self.x + offset_x,
                'y': self.y + offset_y,
                'size': size,
                'lifetime_offset': lifetime_offset,
                'color': (red, 0, 0)
            })

        # Add a central smaller splatter
        self.particles.append({
            'x': self.x,
            'y': self.y,
            'size': random.randint(3, 6),  # Smaller central splatter
            'lifetime_offset': 0,
            'color': (150, 0, 0)
        })

    def update(self, dt):
        self.age += dt
        return self.age < self.lifetime

    def render(self, screen, camera_offset):
        if self.age < self.lifetime:
            for particle in self.particles:
                # Calculate particle lifetime with offset
                particle_lifetime = self.lifetime + particle['lifetime_offset']
                if self.age < particle_lifetime:
                    # Calculate screen position
                    screen_x = int(particle['x'] - camera_offset[0])
                    screen_y = int(particle['y'] - camera_offset[1])

                    # Calculate alpha and size based on age
                    alpha = int(255 * (1 - self.age / particle_lifetime))
                    size_multiplier = 1.0 + (self.age / particle_lifetime)  # Grow over time
                    radius = int(particle['size'] * size_multiplier)

                    # Create surface with alpha for transparency
                    blood_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)

                    # Draw blood particle with alpha
                    color_with_alpha = (*particle['color'], alpha)
                    pygame.draw.circle(blood_surface, color_with_alpha, (radius, radius), radius)

                    # Add some splatter effect (random small circles around the main one)
                    if random.random() < 0.5 and radius > 2:  # 50% chance for additional splatter
                        for _ in range(1):  # Only one additional splatter
                            splatter_x = random.randint(0, radius*2)
                            splatter_y = random.randint(0, radius*2)
                            splatter_size = random.randint(1, 2)  # Smaller splatter
                            pygame.draw.circle(blood_surface, color_with_alpha, 
                                              (splatter_x, splatter_y), splatter_size)

                    # Blit to screen
                    screen.blit(blood_surface, (screen_x - radius, screen_y - radius))
