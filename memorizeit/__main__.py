#!/usr/bin/env python3
"""#### Main

This is main file of MemorizeIT game. Project is created to increase memory
and focus among children or adults who would like to take part in training.
Rules of game are quite simple. You just need to count elements displayed on
screen and remember their type. At the end you will be asked to write down
your results and confront them with exact ones. This will be verified by
marking your answer with proper color (correct - green, not - red). Difficulty
of game can be increased by adding more types of elements to count, mixing
their colors, turning sound off or changing time dedicated to each wave. It is
also more difficult to play normal game mode (instead of static), because
figures are moving which is additional distraction. I wish you enjoyable
experience with game and best results in memory training. Good luck!

Side note: in installation directory there is place called elements where you
can add your custom pictures which will be displayed during static mode
gameplay. Application scales them automatically, so you don't have to worry
about it. If you don't like custom graphics just remove them from elements
directory then figures will be displayed.

License:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import pygame

from memorizeit import gui


def main():
    """Initialize main menu of the application."""
    pygame.init()
    pygame.display.set_caption('MemorizeIT')
    try:
        pygame.display.set_icon(pygame.image.load('images/brain.png'))
    except pygame.error:
        pass
    gui.Menu()


if __name__ == '__main__':
    main()
