import sys
from PIL import Image


def clamp(num):
    """
    Return a "clamped" version of the given num,
    converted to be an int limited to the range 0..255 for 1 byte.
    """
    num = int(num)
    if num < 0:
        return 0
    if num >= 256:
        return 255
    return num


class Pixel(object):
    """
    A pixel at an x,y in a SimpleImage.
    Supports set/get .red .green .blue
    and get .x .y
    """
    def __init__(self, image, x, y):
        self.image = image
        self._x = x
        self._y = y

    def __str__(self):
        return 'r:' + str(self.red) + ' g:' + str(self.green) + ' b:' + str(self.blue)

    # Pillow image stores each pixel color as a (red, green, blue) tuple.
    # So the functions below have to unpack/repack the tuple to change anything.

    @property
    def red(self):
        return self.image.px[self._x, self._y][0]

    @red.setter
    def red(self, value):
        rgb = self.image.px[self._x, self._y]
        self.image.px[self._x, self._y] = (clamp(value), rgb[1], rgb[2])

    @property
    def green(self):
        return self.image.px[self._x, self._y][1]

    @green.setter
    def green(self, value):
        rgb = self.image.px[self._x, self._y]
        self.image.px[self._x, self._y] = (rgb[0], clamp(value), rgb[2])

    @property
    def blue(self):
        return self.image.px[self._x, self._y][2]

    @blue.setter
    def blue(self, value):
        rgb = self.image.px[self._x, self._y]
        self.image.px[self._x, self._y] = (rgb[0], rgb[1], clamp(value))

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y


# color tuples for background color names 'red' 'white' etc.
BACK_COLORS = {
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
}


class SimpleImage(object):
    def __init__(self, filename, width=0, height=0, back_color=None):
        """
        Create a new image. This case works: SimpleImage('foo.jpg')
        To create a blank image use SimpleImage.blank(500, 300)
        The other parameters here are for internal/experimental use.
        """
        # Create pil_image either from file, or making blank
        if filename:
            self.pil_image = Image.open(filename).convert("RGB")
            if self.pil_image.mode != 'RGB':
                raise Exception('Image file is not RGB')
            self._filename = filename  # hold onto
        else:
            if not back_color:
                back_color = 'white'
            color_tuple = BACK_COLORS[back_color]
            if width == 0 or height == 0:
                raise Exception('Creating blank image requires width/height but got {} {}'
                                .format(width, height))
            self.pil_image = Image.new('RGB', (width, height), color_tuple)
        self.px = self.pil_image.load()
        size = self.pil_image.size
        self._width = size[0]
        self._height = size[1]
        self.curr_x = 0
        self.curr_y = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.curr_x < self.width and self.curr_y < self.height:
            x = self.curr_x
            y = self.curr_y
            self.increment_curr_counters()
            return Pixel(self, x, y)
        else:
            self.curr_x = 0
            self.curr_y = 0
            raise StopIteration()

    def increment_curr_counters(self):
        self.curr_x += 1
        if self.curr_x == self.width:
            self.curr_x = 0
            self.curr_y += 1

    @classmethod
    def blank(cls, width, height, back_color=None):
        """Create a new blank image of the given width and height, optional back_color."""
        return SimpleImage('', width, height, back_color=back_color)

    @classmethod
    def file(cls, filename):
        """Create a new image based on a file, alternative to raw constructor."""
        return SimpleImage(filename)

    @property
    def width(self):
        """Width of image in pixels."""
        return self._width

    @property
    def height(self):
        """Height of image in pixels."""
        return self._height

    def get_pixel(self, x, y):
        """
        Returns a Pixel at the given x,y, suitable for getting/setting
        .red .green .blue values.
        """
        if x < 0 or x >= self._width or y < 0 or y >= self.height:
            e = Exception('get_pixel bad coordinate x %d y %d (vs. image width %d height %d)' %
                          (x, y, self._width, self.height))
            raise e
        return Pixel(self, x, y)

    def set_pixel(self, x, y, pixel):
        if x < 0 or x >= self._width or y < 0 or y >= self.height:
            e = Exception('set_pixel bad coordinate x %d y %d (vs. image width %d height %d)' %
                          (x, y, self._width, self.height))
            raise e
        self.px[x, y] = (pixel.red, pixel.green, pixel.blue)

    def set_rgb(self, x, y, red, green, blue):
        """
        Set the pixel at the given x,y to have
        the given red/green/blue values without
        requiring a separate pixel object.
        """
        self.px[x, y] = (red, green, blue)

    def _get_pix_(self, x, y):
        """Get pix RGB tuple (200, 100, 50) for the given x,y."""
        return self.px[x, y]

    def _set_pix_(self, x, y, pix):
        """Set the given pix RGB tuple into the image at the given x,y."""
        self.px[x, y] = pix

    def show(self):
        """Displays the image using an external utility."""
        self.pil_image.show()

    def make_as_big_as(self, image):
        """Resizes image to the shape of the given image"""
        self.pil_image = self.pil_image.resize((image.width, image.height))
        self.px = self.pil_image.load()
        size = self.pil_image.size
        self._width = size[0]
        self._height = size[1]

    def write(self, path):
        """Write image to file"""
        self.pil_image.save(path)

    def copy(self):
        """Returns a deep copy of the SimpleImage object."""
        new_image = SimpleImage.blank(self.width, self.height)
        new_image.pil_image = self.pil_image.copy()
        new_image.px = new_image.pil_image.load()
        return new_image

    def grayscale(image):
        gray = image.copy()

        for pixel in gray:
            avg = (pixel.red + pixel.green + pixel.blue) // 3
            pixel.red = avg
            pixel.green = avg
            pixel.blue = avg
        return gray

    def sepia(image):
        sep = image.copy()

        for pixel in sep:
            og_red = pixel.red
            og_green = pixel.green
            og_blue = pixel.blue

            new_red = int(0.393 * og_red + 0.769 * og_green + 0.189 * og_blue)
            new_green = int(0.349 * og_red + 0.686 * og_green + 0.168 * og_blue)
            new_blue = int(0.272 * og_red + 0.534 * og_green + 0.131 * og_blue)

            pixel.red = min(255, new_red)
            pixel.green = min(255, new_green)
            pixel.blue = min(255, new_blue)

        return sep

    def shrink(image, scale):
        new_width = image.width // scale
        new_height = image.height // scale

        res = SimpleImage.blank(new_width, new_height)

        for y in range(new_height):
            for x in range(new_width):
                og_x = x * scale
                og_y = y * scale

                og_pixel = image.get_pixel(og_x, og_y)
                res_pixel = res.get_pixel(x, y)

                res_pixel.red = og_pixel.red
                res_pixel.green = og_pixel.green
                res_pixel.blue = og_pixel.blue

        return res

    def flip(image, direction):
        flipped = image.copy()
        if direction == 0:
            for x in range(image.width):
                for y in range(image.height):
                    flipped.set_pixel(x, y, image.get_pixel(image.width - 1 - x, y))
        elif direction == 1: 
            for x in range(image.width):
                for y in range(image.height):
                    flipped.set_pixel(x, y, image.get_pixel(x, image.height - 1 - y))
        return flipped

    def blur(image):
        res = image.copy()
        for y in range(1, image.height - 1):
            for x in range(1, image.width - 1):
                total_red = 0
                total_green = 0
                total_blue = 0
                count = 0

                for ny in range(y - 1, y + 2):
                    for nx in range(x - 1, x + 2):
                        if 0 <= nx < image.width and 0 <= ny < image.height:
                            neighbor = image.get_pixel(nx, ny)
                            total_red += neighbor.red
                            total_green += neighbor.green
                            total_blue += neighbor.blue
                            count += 1
                avg_red = total_red // count
                avg_green = total_green // count
                avg_blue = total_blue // count
                pixel = res.get_pixel(x, y)
                pixel.red = avg_red
                pixel.green = avg_green
                pixel.blue = avg_blue
        return res

    def filter(image, channel, intensity):
        res = image.copy()
        for pixel in res:
            if (channel == 'red' and pixel.red > intensity) or (channel == 'green' and pixel.green > intensity) or (channel == 'blue' and pixel.blue > intensity):
                pass
            else:
                avg = (pixel.red + pixel.green + pixel.blue) // 3
                pixel.red = avg
                pixel.green = avg
                pixel.blue = avg
        return res

    def greenscreen(image1, channel, intensity, image2):
        greenscreened = image1.copy()
        image2.make_as_big_as(greenscreened)
        for pixel in greenscreened:
            if channel == 'red' and pixel.red < intensity:
                bg_pixel = image2.get_pixel(pixel.x, pixel.y)
                pixel.red = bg_pixel.red
                pixel.green = bg_pixel.green
                pixel.blue = bg_pixel.blue
            elif channel == 'green' and pixel.green < intensity:
                bg_pixel = image2.get_pixel(pixel.x, pixel.y)
                pixel.red = bg_pixel.red
                pixel.green = bg_pixel.green
                pixel.blue = bg_pixel.blue
            elif channel == 'blue' and pixel.blue < intensity:
                bg_pixel = image2.get_pixel(pixel.x, pixel.y)
                pixel.red = bg_pixel.red
                pixel.green = bg_pixel.green
                pixel.blue = bg_pixel.blue
        return greenscreened


def main():
    """
    main() exercises the features as a test.
    1. With 1 arg like flowers.jpg - opens it
    2. With 0 args, creates a yellow square with
    a green stripe at the right edge.
    """
    args = sys.argv[1:]
    if len(args) == 1:
        image = SimpleImage.file(args[0])
        image.show()
        return

    # Create yellow rectangle, using foreach iterator
    image = SimpleImage.blank(400, 200)
    for pixel in image:
        pixel.red = 255
        pixel.green = 255
        pixel.blue = 0

    # for pixel in image:
    #     print(pixel)

    # Set green stripe using pix access.
    pix = image._get_pix_(0, 0)
    green = (0, pix[1], 0)
    for x in range(image.width - 10, image.width):
        for y in range(image.height):
            image._set_pix_(x, y, green)
    image.show()


if __name__ == '__main__':
    main()
