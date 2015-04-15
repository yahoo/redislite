import redislite

r = redislite.Redis(slaveof="localhost 7000")