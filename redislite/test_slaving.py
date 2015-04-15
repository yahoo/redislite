import redislite.client

r = redislite.Redis(slaveof="localhost 7000")