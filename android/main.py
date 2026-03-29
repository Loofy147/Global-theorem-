import os, sys
# Ensure we can import from research/ and other local dirs
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Kivy Framework Imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

# TGI Mobile Core
from research.mobile_tgi_agent import MobileTGIAgent

class TGIMobileApp(App):
    def build(self):
        self.title = "TGI Mobile - Topological General Intelligence"
        self.agent = MobileTGIAgent()

        # Root Layout
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 1. Header Area (Hardware Stats)
        self.hw_label = Label(text="HW Stats: Loading...", size_hint_y=None, height=40, color=(0, 1, 0, 1))
        root.add_widget(self.hw_label)

        # 2. Console/Output Area
        self.scroll = ScrollView(size_hint=(1, 0.7))
        self.output = Label(
            text="═══ TGI MANIFOLD CONSOLE ═══\nWelcome to Phase 6 Mobile TGI.\n\n",
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        self.output.bind(texture_size=self.output.setter('size'))
        self.scroll.add_widget(self.output)
        root.add_widget(self.scroll)

        # 3. Input Area
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)
        self.query_input = TextInput(
            text="Check system health and notify",
            multiline=False,
            size_hint_x=0.8
        )
        self.query_input.bind(on_text_validate=self.on_query)

        submit_btn = Button(text="QUERY", size_hint_x=0.2)
        submit_btn.bind(on_press=self.on_query)

        input_layout.add_widget(self.query_input)
        input_layout.add_widget(submit_btn)
        root.add_widget(input_layout)

        # Update hardware periodically
        Clock.schedule_interval(self.update_hardware, 2.0)

        return root

    def update_hardware(self, dt):
        state = self.agent.hardware.get_system_state()
        coord = self.agent.hardware.map_to_coordinate()
        entropy = self.agent.hardware.measure_thermal_entropy()
        self.hw_label.text = f"CPU: {state['cpu']}% | RAM: {state['memory']:.1f}% | Bat: {state['battery']}% | Coord: {coord} | S: {entropy:.4f}"

    def on_query(self, instance):
        query_text = self.query_input.text
        if not query_text: return

        # Process through Mobile TGI
        self.append_output(f"\n> QUERY: {query_text}")

        # This will be a blocking call in this skeleton, but should be async in full version
        res = self.agent.mobile_query(query_text)

        self.append_output(f"[LIFT] Intent Coord: {res['hw_coord']}")
        self.append_output(f"[TGI] {res['tgi_raw']}")
        self.append_output(f"[ACTION] {res['resolved_action']['action']} (I={res['resolved_action']['intensity']})")

        self.query_input.text = ""

    def append_output(self, text):
        self.output.text += text + "\n"
        # Auto-scroll to bottom
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0))

if __name__ == "__main__":
    TGIMobileApp().run()
