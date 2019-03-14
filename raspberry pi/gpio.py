import RPi.GPIO as gpio

import config

class Gpio:
    def __init__(self):
        # GPIO引脚定义
        self.ud_enable = 16
        self.rl_enable = 0
        self.fb_enable = 0
        self.enable = [self.ud_enable, self.rl_enable, self.fb_enable]
        self.up_dir = 20
        self.down_dir = 0
        self.up_step = 21
        self.down_step = 0
        gpio.setmode(gpio.BOARD)
        gpio.setup([*self.enable, self.up_dir, self.down_dir, self.up_step, self.down_step], gpio.OUT)


    def camera_off(self):
        pass

    def camera_on(self, x):
        pass

    def light(self, color):
        pass

    def usdelay(self, i):
        while i:
            for x in range(325):
                pass
            i -= 1

    def move(self, move):
        gpio.output(self.enable, 0)

        # Enable 同时使能相对两面
        enable = {
            'U': self.ud_enable,
            'R': self.rl_enable,
            'F': self.fb_enable,
            'D': self.ud_enable,
            'L': self.rl_enable,
            'B': self.fb_enable,
        }
        gpio.output(enable[move[0]], 1)

        if move[1] == '2':
            gpio.output([self.up_dir, self.down_dir], 1)
            if move[0] in ['U', 'R', 'F']:
                for i in range(100 * config.div):
                    gpio.output(self.up_step, 1)
                    self.usdelay(800)
                    gpio.output(self.up_step, 0)
                    self.usdelay(800)
            else:
                for i in range(100 * config.div):
                    gpio.output(self.down_step, 1)
                    self.usdelay(800)
                    gpio.output(self.down_step, 0)
                    self.usdelay(800)
        else:
            if move[1] == '1':
                gpio.output([self.up_dir, self.down_dir], config.direction[move[0]] ^ 1)
            else:
                gpio.output([self.up_dir, self.down_dir], config.direction[move[0]] ^ 0)
            if move[0] in ['U', 'R', 'F']:
                for i in range(50 * config.div):
                    gpio.output(self.up_step, 1)
                    self.usdelay(800)
                    gpio.output(self.up_step, 0)
                    self.usdelay(800)
            else:
                for i in range(5 * config.div):
                    gpio.output(self.down_step, 1)
                    self.usdelay(800)
                    gpio.output(self.down_step, 0)
                    self.usdelay(800)


        #gpio.output(self.up_step, step[move[0]] ^ 1)
        #gpio.output(self.down_step, step[move[0]] ^ 0)


