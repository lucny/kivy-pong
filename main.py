from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector


# Třída pro míček, dědí z předka Widget
class Ball(Widget):
    pass
    # Vlastnosti ukládají rychlost míčku ve dvou osách
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    # Vlastnost ukládá rychlost míčku ve dvou osách ve formě Listu
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    # Metoda pro aktualizaci pozice míčku
    def move(self):
        # Objekt Vector použije rozbalovací operátor a vytvoří vektor na základě rychlosti v ose x a y
        # Získanou pozici přičte k dosavadní pozici míčku
        self.pos = Vector(*self.velocity) + self.pos


# Třída pro pálku, dědí z předka Widget
class Paddle(Widget):
    score = NumericProperty(0)  # Skóre hráče

    # Metoda pro pohyb pálky nahoru
    def move_up(self):
        self.y += 10  # Pohyb nahoru o 10 pixelů

    # Metoda pro pohyb pálky dolů
    def move_down(self):
        self.y -= 10  # Pohyb dolů o 10 pixelů

    # Metoda řeší odraz míčku od pálky
    def bounce_ball(self, ball):
        # V případě kolize míčku s objektem pálky
        if self.collide_widget(ball):
            # Zjistí rychlost míčku v obou osách
            vx, vy = ball.velocity
            # Vypočte odchylku středu míčku od středu pálky, která ovlivní úhel odpálení míčku
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            # Inverze rychlosti v ose x a připočtení odchylky v ose y
            vel = Vector(-1 * vx, vy)
            ball.velocity = vel.x, vel.y + offset


# Hlavní třída pro Pong hru, dědí z předka Widget
class PongGame(Widget):
    # Příprava vlastností pro uložení zhákladních objektů hry
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    # Konsktruktor
    def __init__(self, **kwargs):
        # Dědičnost - vyvolání konstruktoru předka - v tomto případě třídy Widget
        super(PongGame, self).__init__(**kwargs)
        # Získání instance klávesnice z aktuálního okna,
        # •	self._keyboard_closed: Při ztrátě fokusu klávesnice bude volána tato metoda
        # •	self: Tento argument specifikuje, kdo je "requester" klávesnice, tedy objekt, který o klávesnici požádal.
        # V tomto případě to je instance třídy, ve které je tento kód umístěn.
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        # •	self._keyboard.bind(...): Tato metoda se používá k navázání události klávesnice na konkrétní funkci nebo metodu.
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    # Servis míčku - standardně je míčku udělena rychlost 6 v ose x a 0 v ose y
    def serve_ball(self, vel=(6, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    # Aktualizace hry v rámci jednoho snímku, dt (delta time, snímková frekvence)
    def update(self, dt):
        self.ball.move()
        # Kontroluje případný odraz míčku od obou pálek
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)
        # Omezení pohybu pálek (nesmí se dostat mimo horní a dolní mantinel)
        self.player1.y = min(self.height - self.player1.height, max(0, self.player1.y))
        self.player2.y = min(self.height - self.player2.height, max(0, self.player2.y))

        # Odraz míčku od horního a dolního mantinelu - inverze rychlosti v ose y
        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1

        # Jestliže míček nebyl hráčem na levé straně odražen - navýšení skóre pravého hráče, nové podání
        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball(vel=(6, 0))
        # Jestliže míček nebyl hráčem na pravé straně odražen - navýšení skóre levého hráče, nové podání
        if self.ball.right > self.width:
            self.player1.score += 1
            self.serve_ball(vel=(-6, 0))

    # Ovládání pálek pomocí dotyků/myši
    def on_touch_move(self, touch):
        # V případě, že byl zaznamenán dotyk v levé třetině obrazovky
        if touch.x < self.width / 3:
            # Pálka hráče 1 bude přesunuta v ose y podle zaznamenané souřadnice dotky/kurzoru
            self.player1.center_y = touch.y
        # V případě, že byl zaznamenán dotyk v pravé třetině obrazovky
        if touch.x > self.width - self.width / 3:
            # Pálka hráče 2 bude přesunuta v ose y podle zaznamenané souřadnice dotky/kurzoru
            self.player2.center_y = touch.y

    # Rozvázání propojené akce klávesnice v případě ztráty fokusu okna
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    # Zachycení události při stisku kláves, pohyby pálek
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # Klávesy pro prvního hráče
        if keycode[1] == 'w':
            self.player1.move_up()
        elif keycode[1] == 's':
            self.player1.move_down()
        # Klávesy pro druhého hráče
        elif keycode[1] == 'up':
            self.player2.move_up()
        elif keycode[1] == 'down':
            self.player2.move_down()


# Třída pro spuštění hry
class PongApp(App):
    # Sestavení hry včetně grafického prostředí (pong.kv)
    def build(self):
        # Vytvoření instance hry s využitím konstruktoru
        game = PongGame()
        # Úvodní podání
        game.serve_ball()
        # Nastavení snímkové frekvence, obnova stavu hry prostřednictvím metody update
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


# Spuštění hry
if __name__ == '__main__':
    PongApp().run()
