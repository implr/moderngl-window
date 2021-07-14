from .base import BaseVideoCapture
import subprocess
import moderngl
import logging

class FFmpegCapture(BaseVideoCapture):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._ffmpeg = None
    
    def _start_func(self) -> bool:

        pix_fmt = 'rgb24'   # 3 component, 1 byte per color -> 24 bit
                            
        # for the framebuffer is easier because i can read 3 component even if
        # the color attachment has less components
        if isinstance(self._source, moderngl.Texture) and self._components == 4:
            pix_fmt = 'rgba' # 4 component , 1 byte per color -> 32 bit

        command = [
            'ffmpeg',
            '-hide_banner',
            '-loglevel', 'error', '-stats', # less verbose, only stats of recording
            '-y',  # (optional) overwrite output file if it exists
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', f'{self._width}x{self._height}',  # size of one frame
            '-pix_fmt', pix_fmt,
            '-r', f'{self._framerate}',  # frames per second
            '-i', '-',  # The imput comes from a pipe
            '-vf', 'vflip',
            '-an',  # Tells FFMPEG not to expect any audio
            self._filename,
        ]
        
        # ffmpeg binary need to be on the PATH.
        try:
            self._ffmpeg = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                bufsize=0
            )
        except FileNotFoundError:
            logging.info("ffmpeg command not found. Be sure to add it to PATH")
            return
        
        return True
    
    def _release_func(self):
        self._ffmpeg.stdin.close()
        ret = self._ffmpeg.wait()
    
    def _dump_frame(self, frame):
        self._ffmpeg.stdin.write(frame)
