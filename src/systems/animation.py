"""
Animation System - Visual Effects Management
============================================

Centralized system for handling all visual effects like explosions,
muzzle flashes, bullet impacts, etc.
"""

import pygame
import random
import math
from utils.constants import WHITE, YELLOW, RED, BLACK


class Effect:
    """Base class for all visual effects"""

    def __init__(self, x, y, duration, **kwargs):
        self.x = x
        self.y = y
        self.duration = duration
        self.start_time = pygame.time.get_ticks() / 1000.0
        self.kwargs = kwargs

    @property
    def progress(self):
        """Get animation progress (0.0 to 1.0)"""
        current_time = pygame.time.get_ticks() / 1000.0
        elapsed = current_time - self.start_time
        return min(1.0, elapsed / self.duration)

    @property
    def is_finished(self):
        """Check if effect is finished"""
        return self.progress >= 1.0

    def render(self, screen, camera_offset=(0, 0)):
        """Render the effect - to be implemented by subclasses"""
        pass


class MuzzleFlashEffect(Effect):
    """Muzzle flash animation effect"""

    def __init__(self, x, y, duration=0.1, **kwargs):
        super().__init__(x, y, duration, **kwargs)

    def render(self, screen, camera_offset=(0, 0)):
        if self.is_finished:
            return

        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])

        # Flash gets smaller over time
        size_multiplier = 1.0 - self.progress
        base_radius = 12
        radius = int(base_radius * size_multiplier)

        if radius > 0:
            # Outer yellow flash
            flash_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            alpha = int(255 * (1.0 - self.progress))
            pygame.draw.circle(flash_surface, (255, 255, 0, alpha), (radius, radius), radius)
            screen.blit(flash_surface, (screen_x - radius, screen_y - radius))

            # Inner white core
            inner_radius = max(1, radius // 2)
            core_surface = pygame.Surface((inner_radius * 2, inner_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(core_surface, (255, 255, 255, alpha), (inner_radius, inner_radius), inner_radius)
            screen.blit(core_surface, (screen_x - inner_radius, screen_y - inner_radius))


class BulletImpactEffect(Effect):
    """Bullet impact sparks effect"""

    def __init__(self, x, y, duration=0.2, **kwargs):
        super().__init__(x, y, duration, **kwargs)
        self.color = kwargs.get('color', (255, 255, 255))

    def render(self, screen, camera_offset=(0, 0)):
        if self.is_finished:
            return

        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])

        alpha = int(255 * (1.0 - self.progress))
        color_with_alpha = (*self.color, alpha)

        # Draw sparks as small lines
        spark_length = int(6 * (1.0 - self.progress))
        if spark_length > 0:
            # Create surface for alpha blending
            spark_surface = pygame.Surface((spark_length * 4, spark_length * 4), pygame.SRCALPHA)

            # Draw cross pattern
            center = spark_length * 2
            pygame.draw.line(spark_surface, color_with_alpha,
                             (center - spark_length, center), (center + spark_length, center), 2)
            pygame.draw.line(spark_surface, color_with_alpha,
                             (center, center - spark_length), (center, center + spark_length), 2)

            screen.blit(spark_surface, (screen_x - center, screen_y - center))


class BloodSplatterEffect(Effect):
    """Blood splatter effect with multiple particles"""

    def __init__(self, x, y, duration=0.8, **kwargs):
        super().__init__(x, y, duration, **kwargs)

        # Create blood particles
        self.particles = []
        num_particles = random.randint(4, 8)

        for _ in range(num_particles):
            self.particles.append({
                'offset_x': random.randint(-12, 12),
                'offset_y': random.randint(-12, 12),
                'size': random.randint(2, 6),
                'color': (random.randint(120, 180), 0, 0),
                'lifetime_multiplier': random.uniform(0.7, 1.3)
            })

    def render(self, screen, camera_offset=(0, 0)):
        if self.is_finished:
            return

        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])

        for particle in self.particles:
            # Calculate particle-specific progress
            particle_progress = min(1.0, self.progress * particle['lifetime_multiplier'])

            if particle_progress < 1.0:
                part_x = screen_x + particle['offset_x']
                part_y = screen_y + particle['offset_y']

                alpha = int(255 * (1.0 - particle_progress))
                size = int(particle['size'] * (1.0 + particle_progress * 0.5))  # Grow slightly

                if alpha > 0 and size > 0:
                    blood_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    color_with_alpha = (*particle['color'], alpha)
                    pygame.draw.circle(blood_surface, color_with_alpha, (size, size), size)
                    screen.blit(blood_surface, (part_x - size, part_y - size))


class ExplosionEffect(Effect):
    """Explosion effect with particles"""

    def __init__(self, x, y, duration=0.6, **kwargs):
        super().__init__(x, y, duration, **kwargs)
        self.max_radius = kwargs.get('radius', 50)

        # Create explosion particles
        self.particles = []
        num_particles = random.randint(8, 15)

        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 80)
            self.particles.append({
                'start_x': x,
                'start_y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.randint(3, 8),
                'color': random.choice([
                    (255, 255, 100),  # Bright yellow
                    (255, 200, 0),  # Orange
                    (255, 100, 0),  # Dark orange
                    (200, 50, 0)  # Red
                ])
            })

    def render(self, screen, camera_offset=(0, 0)):
        if self.is_finished:
            return

        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])

        # Main explosion circle
        current_radius = int(self.max_radius * self.progress)
        alpha = max(0, int(255 * (1.0 - self.progress)))

        if current_radius > 0 and alpha > 0:
            # Outer blast wave
            blast_surface = pygame.Surface((current_radius * 2, current_radius * 2), pygame.SRCALPHA)
            blast_color = (255, 150, 0, alpha // 2)
            pygame.draw.circle(blast_surface, blast_color, (current_radius, current_radius), current_radius)
            screen.blit(blast_surface, (screen_x - current_radius, screen_y - current_radius))

            # Inner core
            inner_radius = max(1, current_radius // 2)
            core_surface = pygame.Surface((inner_radius * 2, inner_radius * 2), pygame.SRCALPHA)
            core_color = (255, 255, 200, alpha)
            pygame.draw.circle(core_surface, core_color, (inner_radius, inner_radius), inner_radius)
            screen.blit(core_surface, (screen_x - inner_radius, screen_y - inner_radius))

        # Render flying particles
        for particle in self.particles:
            # Calculate particle position
            time_factor = self.progress
            part_x = particle['start_x'] + particle['vx'] * time_factor * self.duration
            part_y = particle['start_y'] + particle['vy'] * time_factor * self.duration

            # Add gravity to particles
            part_y += 0.5 * 100 * (time_factor * self.duration) ** 2

            part_screen_x = int(part_x - camera_offset[0])
            part_screen_y = int(part_y - camera_offset[1])

            part_alpha = max(0, int(255 * (1.0 - self.progress)))
            part_size = max(1, int(particle['size'] * (1.0 - self.progress * 0.5)))

            if part_alpha > 0 and part_size > 0:
                particle_surface = pygame.Surface((part_size * 2, part_size * 2), pygame.SRCALPHA)
                particle_color = (*particle['color'], part_alpha)
                pygame.draw.circle(particle_surface, particle_color, (part_size, part_size), part_size)
                screen.blit(particle_surface, (part_screen_x - part_size, part_screen_y - part_size))


class AnimationSystem:
    """Central animation system for managing all visual effects"""

    def __init__(self):
        self.effects = []
        self.effect_types = {
            'muzzle_flash': MuzzleFlashEffect,
            'bullet_impact': BulletImpactEffect,
            'blood_splatter': BloodSplatterEffect,
            'explosion': ExplosionEffect
        }

    def add_effect(self, effect_type, x, y, duration=1.0, **kwargs):
        """Add a new visual effect"""
        if effect_type in self.effect_types:
            effect_class = self.effect_types[effect_type]
            effect = effect_class(x, y, duration, **kwargs)
            self.effects.append(effect)

    def update(self, dt):
        """Update and remove finished effects"""
        self.effects = [effect for effect in self.effects if not effect.is_finished]

    def render(self, screen, camera_offset=(0, 0)):
        """Render all active effects"""
        for effect in self.effects:
            effect.render(screen, camera_offset)

    def clear(self):
        """Clear all effects"""
        self.effects.clear()


# Global animation system instance
animation_system = AnimationSystem()