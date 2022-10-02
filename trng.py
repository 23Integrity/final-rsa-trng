from subprocess import Popen, PIPE
import random


def generate_random(amount_of_bits: int = 8):
    p = Popen('True Random Number Generator.exe ' + str(amount_of_bits), stdout=PIPE, stdin=PIPE)
    result = int.from_bytes(p.stdout.readline().strip(), byteorder='big')
    return bytes(result - random.randint(0, 1000))
