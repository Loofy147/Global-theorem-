from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import os

class TGIMobileApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Title
        self.layout.add_widget(Label(text="TGI MOBILE — FSO Codex Governance", font_size='20sp', size_hint_y=None, height=50))

        # Laws Display
        self.scroll = ScrollView(size_hint=(1, 1))
        self.laws_label = Label(
            text=self.load_laws(),
            size_hint_y=None,
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        self.laws_label.bind(texture_size=self.laws_label.setter('size'))
        self.scroll.add_widget(self.laws_label)
        self.layout.add_widget(self.scroll)

        # Status
        self.status_label = Label(text="Status: Topology Synchronized", size_hint_y=None, height=30)
        self.layout.add_widget(self.status_label)

        return self.layout

    def load_laws(self):
        try:
            # In Android, we might need a relative path or asset mapping
            # For now, we simulate the Codex content if the file is missing
            if os.path.exists("docs/LAWS.md"):
                with open("docs/LAWS.md", "r") as f:
                    return f.read()
            else:
                return "FSO CODEX: Law I (Parity), Law II (Density), Law III (Closure)... [Codex File Missing]"
        except Exception as e:
            return f"Error loading laws: {e}"

if __name__ == "__main__":
    TGIMobileApp().run()
