import math

import pygame
from pygame.rect import Rect

from pygame_widgets.rect import draw_rounded_rect
from pygame_widgets.widget import WidgetBase


class Checkbox(WidgetBase):
    def __init__(self, win, x, y, width, height, items, **kwargs):
        """ A collection of buttons

        :param win: Surface on which to draw
        :type win: pygame.Surface
        :param x: X-coordinate of top left
        :type x: int
        :param y: Y-coordinate of top left
        :type y: int
        :param width: Width of button
        :type width: int
        :param height: Height of button
        :type height: int
        :param items: Names of list items
        :type items: tuple of str
        :param kwargs: Optional parameters
        """
        super().__init__(win, x, y, width, height)

        self.items = items
        self.rows = len(items)
        self.rowHeight = self.height // self.rows
        self.selected = [False for _ in range(self.rows)]

        # Border
        self.borderThickness = kwargs.get('borderThickness', 15)
        self.borderColour = kwargs.get('borderColour', (0, 0, 0))
        self.radius = kwargs.get('radius', 0)

        # Checkbox color and size
        self.boxSize = kwargs.get('boxSize', self.height / self.rows // 2)
        self.boxColour = kwargs.get('boxColour', (0, 0, 0))
        self.boxColour2 = kwargs.get('boxColour', (155, 155, 155))

        # Colour background
        self.colour = kwargs.get('colour', (255, 255, 255))
        self.colour2 = kwargs.get('colour', (250, 250, 250))
        self.colour_hover = kwargs.get('colour', (210, 210, 200))

        # Alternating colours: overrides colour
        self.colour1 = kwargs.get('colour1', self.colour)
        self.colour2 = kwargs.get('colour2', self.colour2)

        # Text
        self.textColour = kwargs.get('textColour', (0, 0, 0))
        self.fontSize = kwargs.get('fontSize', 14)
        self.font = kwargs.get('font', pygame.font.SysFont('calibri', self.fontSize))
        self.texts = [self.font.render(self.items[row], True, self.textColour) for row in range(self.rows)]
        self.textRects = self.createTextRects()

        self.clicked = False

        self.boxes = self.createBoxLocations()

    def createTextRects(self):
        textRects = []
        for row in range(self.rows):
            textRects.append(
                self.texts[row].get_rect(
                    center=(
                        self.x + self.boxSize * 2 + (self.width - self.boxSize * 2) // 2,
                        self.y + self.rowHeight * row + self.rowHeight // 2
                    )
                )
            )

        return textRects

    def createBoxLocations(self):
        boxes = []
        for row in range(self.rows):
            boxes.append(pygame.Rect(
                self.x + self.boxSize,
                self.y + self.rowHeight * row + self.boxSize // 2,
                self.boxSize, self.boxSize
            ))
        return boxes

    def check_selected(self, index):
        return self.selected[index]

    def listen(self, events):
        """ Wait for inputs

        :param events: Use pygame.event.get()
        :type events: list of pygame.event.Event
        """
        if not self.hidden:
            pressed = pygame.mouse.get_pressed()[0]
            x, y = pygame.mouse.get_pos()

            if self.contains(x, y):
                if pressed:
                    if not self.clicked:
                        self.clicked = True
                        for row in range(self.rows):
                            background_rect = Rect(self.x, self.y + self.rowHeight * row, self.width, self.rowHeight)
                            if background_rect.collidepoint(x, y):
                                self.selected[row] = not self.selected[row]

                elif self.clicked:
                    self.clicked = False
            elif not pressed:
                self.clicked = False

    def draw(self):
        """ Display to surface """
        if not self.hidden:
            for row in range(self.rows):
                idle_color = self.colour1 if not row % 2 else self.colour2
                background_rect = Rect(self.x, self.y + self.rowHeight * row, self.width, self.rowHeight)
                hover = self.check_hover(pygame.mouse.get_pos(), background_rect)
                draw_rounded_rect(
                    self.win, self.colour_hover if hover else idle_color, background_rect,
                    border_radius=self.radius
                )

                draw_rounded_rect(
                    self.win, self.boxColour,
                    self.boxes[row],
                    border_radius=1
                )
                if self.selected[row]:
                    draw_rounded_rect(
                        self.win, self.boxColour2,
                        self.boxes[row],
                        border_radius=5
                    )

                self.win.blit(self.texts[row], self.textRects[row])

    def getSelected(self):
        return [self.items[row] for row in range(self.rows) if self.selected[row]]

    def check_hover(self, mouse_pos: tuple, rect: Rect):
        return rect.contains(Rect(mouse_pos, (1, 1)))


class Radio(WidgetBase):
    def __init__(self, win, x, y, width, height, items, **kwargs):
        super().__init__(win, x, y, width, height)

        self.items = items
        self.rows = len(items)
        self.rowHeight = self.height // self.rows
        self.selected = kwargs.get('default', 0)

        # Border
        self.borderThickness = kwargs.get('borderThickness', 3)
        self.borderColour = kwargs.get('borderColour', (0, 0, 0))
        self.radius = kwargs.get('radius', 0)

        # Radio
        self.circleRadius = kwargs.get('circleRadius', self.height / self.rows // 6)
        self.circleThickness = kwargs.get('circleThickness', 3)
        self.circleColour = kwargs.get('circleColour', (0, 0, 0))

        # Colour
        self.colour = kwargs.get('colour', (255, 255, 255))

        # Alternating colours: overrides colour
        self.colour1 = kwargs.get('colour1', self.colour)
        self.colour2 = kwargs.get('colour2', self.colour)

        # Text
        self.textColour = kwargs.get('textColour', (0, 0, 0))
        self.fontSize = kwargs.get('fontSize', 20)
        self.font = kwargs.get('font', pygame.font.SysFont('calibri', self.fontSize))
        self.texts = [self.font.render(self.items[row], True, self.textColour) for row in range(self.rows)]
        self.textRects = self.createTextRects()

        self.clicked = False

        self.circles = self.createCircleLocations()

    def createTextRects(self):
        textRects = []
        for row in range(self.rows):
            textRects.append(
                self.texts[row].get_rect(
                    center=(
                        self.x + self.circleRadius * 6 + (self.width - self.circleRadius * 6) // 2,
                        self.y + self.rowHeight * row + self.rowHeight // 2
                    )
                )
            )

        return textRects

    def createCircleLocations(self):
        circles = []
        for row in range(self.rows):
            circles.append((
                self.x + self.circleRadius * 3,
                self.y + self.rowHeight * row + self.rowHeight // 2,
            ))
        return circles

    def listen(self, events):
        """ Wait for inputs

        :param events: Use pygame.event.get()
        :type events: list of pygame.event.Event
        """
        if not self.hidden:
            pressed = pygame.mouse.get_pressed()[0]
            x, y = pygame.mouse.get_pos()

            if self.contains(x, y):
                if pressed:
                    if not self.clicked:
                        self.clicked = True
                        for row in range(self.rows):
                            if math.sqrt((self.circles[row][0] - x) ** 2 +
                                         (self.circles[row][1] - y) ** 2) <= self.circleRadius:
                                self.selected = row

                elif self.clicked:
                    self.clicked = False

            elif not pressed:
                self.clicked = False

    def draw(self):
        """ Display to surface """
        if not self.hidden:
            for row in range(self.rows):
                colour = self.colour1 if not row % 2 else self.colour2
                if row == 0:
                    pygame.draw.rect(
                        self.win, colour, (self.x, self.y + self.rowHeight * row, self.width, self.rowHeight),
                        border_top_left_radius=self.radius, border_top_right_radius=self.radius
                    )

                elif row == self.rows - 1:
                    pygame.draw.rect(
                        self.win, colour, (self.x, self.y + self.rowHeight * row, self.width, self.rowHeight),
                        border_bottom_left_radius=self.radius, border_bottom_right_radius=self.radius
                    )

                else:
                    pygame.draw.rect(
                        self.win, colour, (self.x, self.y + self.rowHeight * row, self.width, self.rowHeight)
                    )

                width = 0 if row == self.selected else self.circleThickness
                pygame.draw.circle(
                    self.win, self.circleColour,
                    self.circles[row], self.circleRadius,
                    width=width
                )

                self.win.blit(self.texts[row], self.textRects[row])


if __name__ == '__main__':
    pygame.init()
    win = pygame.display.set_mode((1000, 800))

    checkbox = Checkbox(win, 100, 100, 400, 300, ('Apples', 'Bananas', 'Pears'), colour1=(0, 180, 0),
                        colour2=(0, 50, 200), fontSize=30, radius=10)
    radio = Radio(win, 550, 400, 400, 300, ('Apples', 'Bananas', 'Pears'), colour1=(0, 180, 0),
                  colour2=(0, 50, 200), fontSize=30, radius=10)

    run = True
    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
                quit()

        win.fill((255, 255, 255))

        checkbox.listen(events)
        checkbox.draw()

        radio.listen(events)
        radio.draw()

        pygame.display.update()
