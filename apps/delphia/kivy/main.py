from kivy.lang import Builder
from kivy.properties import (
    StringProperty, NumericProperty, BooleanProperty, ListProperty, ObjectProperty
)
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from pathlib import Path
from datetime import date
import os, json
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from functools import partial
# Force a valid DPI/density and a stable mouse input provider
from kivy.config import Config
import time

Config.set('graphics', 'dpi', '160')  # density = dpi/160 => 1.0
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # avoids hover/multitouch quirks
Config.write()

print("Current working directory:", os.getcwd())
print("Files in directory:", os.listdir(os.getcwd()))
print("Current working directory:", os.getcwd())
print("Files in directory:", os.listdir(os.getcwd()))

# ----------------------------
# Clickable text label (for menu-like buttons)
# ----------------------------
class MenuLabel(MDLabel, ButtonBehavior):
    pass

# ----------------------------
# Simple screens (KV provides layout)
# ----------------------------
class HomeScreen(Screen): pass
class ProteinScreen(Screen): pass
class WaterScreen(Screen): pass
class CaloriesScreen(Screen): pass
class MealsScreen(MDScreen): pass
class ProfileScreen(Screen): pass
class SportsScreen(Screen): pass
class CommunityScreen(Screen): pass
class FreeTrainingScreen(Screen): pass

# ----------------------------
# Menu row (used in nav dropdown)
# ----------------------------
class MenuRow(BoxLayout, ButtonBehavior):
    text = StringProperty("")
    on_release_callback = ObjectProperty(None)
    def on_release(self):
        if self.on_release_callback:
            self.on_release_callback()

# ----------------------------
# Workouts screen (complete: all categories, all dropdowns, equipment per row)
# ----------------------------
class WorkoutsScreen(Screen):
    def on_kv_post(self, base_widget):
        # Colors and constants
        self.BLACK = (0, 0, 0, 1)
        self.SILVER = (0.9, 0.9, 0.9, 1)
        self.WHITE = (1, 1, 1, 1)
        self.ALL_INPUTS = ["sets", "reps", "weight", "duration", "distance", "incline"]

        # Dropdown state
        self.menus = {}
        self._active_menu = None

        # Seeded catalogs (your full taxonomy)
        self.exercises_by_category = {
            "Strength Training": ["Back Squat","Front Squat","Deadlift","Romanian Deadlift","Bench Press","Incline Bench Press",
                "Overhead Press","Push Press","Bent-Over Row","Weighted Pull-Up","Weighted Dip","Hip Thrust",
                "Farmer’s Walk","T-Bar Row","Trap Bar Deadlift","Split Squat","Bulgarian Split Squat","Cable Row",
                "Lat Pulldown","Chest Fly","Hammer Curl","EZ-Bar Curl","Skull Crushers","Triceps Pushdown",
                "Kettlebell Swing","Goblet Squat","Suitcase Carry","Sled Push","Sled Drag","Push-Up","Pull-Up","Dip","Inverted Row"],
            "Cardiovascular Training": ["Running (Treadmill)","Jogging","Sprinting","Cycling (Upright)","Spin Bike","Recumbent Bike",
                "Air Bike","Elliptical","Rowing Machine","Stair Climber","Vertical Climber","Jump Rope",
                "Power Walk","Incline Walk","Outdoor Cycling","Trail Running","Rucking"],
            "Recovery & Repair": ["Foam Roll Quads","Foam Roll Lats","Foam Roll Calves","Foam Roll IT Band","Massage Ball Release",
                "Stretching Strap Routine","Yoga Restorative Flow","Breathwork Recovery","Cold Stretch Routine"],
            "Flexibility and Mobility": ["Yoga Sun Salutation","Downward Dog","Child’s Pose","Pigeon Stretch","Hip Flexor Stretch",
                "Hamstring Stretch","Quad Stretch","Calf Stretch","Thoracic Rotation","Shoulder Dislocates (Band)",
                "Ankle Dorsiflexion","90/90 Hip Switch","Cat-Cow","World’s Greatest Stretch","Deep Squat Hold",
                "Wrist Mobility","Neck Mobility","Figure-Four Stretch","Lunge with Reach"],
            "High-Intensity Interval Training (HIIT)": ["Sprint Intervals","Row Intervals","Bike Intervals","Kettlebell Swing Intervals",
                "Burpee Intervals","Battle Rope Waves","Box Jump Intervals","Thruster Intervals","Wall Ball Intervals",
                "Jump Squat Intervals","Mountain Climber Intervals","EMOM Mix"],
            "Functional Training": ["Squat","Deadlift","Hip Hinge","Lunge","Step-Up","Farmer’s Carry","Suitcase Carry","Overhead Carry",
                "Turkish Get-Up","Kettlebell Swing","Medicine Ball Slam","Sandbag Clean","Sandbag Shouldering",
                "TRX Row","TRX Push-Up","Landmine Squat","Landmine Press","Sled Push","Sled Drag","Bear Crawl",
                "Box Step-Up","Pallof Press"],
            "Group Fitness Classes": ["Spin Class","Boot Camp","Circuit Training","BodyPump","Step Aerobics","Dance Fitness (Zumba)",
                "Kickboxing Class","Aqua Aerobics","HIIT Class","Strength Class","Core Burn","Pilates Mat Class",
                "Yoga Vinyasa","Yoga Yin","Barre","TRX Suspension Class","Rowing Class","Mobility Flow"],
            "Mind-Body Workouts": ["Yoga (Hatha)","Yoga (Vinyasa)","Yoga (Yin)","Yoga (Restorative)","Tai Chi","Qi Gong",
                "Pilates Mat","Pilates Reformer","Breathwork Session","Guided Meditation","Somatic Movement",
                "Mindful Walking","Yoga Nidra"],
            # Equipment stays in the catalog for selection (per-row dropdown), not as a UI section
            "Equipment": ["Treadmill","Curved Treadmill","Upright Bike","Recumbent Bike","Spin Bike","Air Bike","Elliptical",
                "Rowing Machine","Stair Climber","Vertical Climber","Jump Rope","Chest Press Machine","Pec Deck",
                "Cable Crossover","Lat Pulldown","Seated Row","Assisted Pull-Up Machine","Leg Press","Leg Curl Machine",
                "Leg Extension Machine","Hip Abduction Machine","Hip Adduction Machine","Glute Kickback Machine",
                "Standing Calf Raise Machine","Smith Machine","Shoulder Press Machine","Chest Fly Machine","Dumbbells",
                "Barbell","EZ Curl Bar","Trap Bar","Kettlebell","Weight Plates","Flat Bench","Incline Bench",
                "Decline Bench","Adjustable Bench","Power Rack","Pull-Up Bar","Dip Bars","Medicine Ball","Slam Ball",
                "Battle Ropes","Sandbag","Resistance Bands","TRX Suspension Trainer","Foam Roller","Massage Stick",
                "Yoga Mat","Stability Ball","Bosu Ball","Ab Wheel Roller","All-in-One Home Gym","Sled Push"]
        }
        self.user_added_exercises = {k: [] for k in self.exercises_by_category}
        self.user_added_equipment = []

        # Prebuilt numeric input menus (stable, caller set on open)
        self.sets_menu = self._make_simple_menu([str(i) for i in range(1, 101)])
        self.reps_menu = self._make_simple_menu([str(i) for i in range(1, 1001)])
        self.weight_menu = self._make_simple_menu([f"{i} lbs" for i in range(1, 2001)])
        self.duration_menu = self._make_simple_menu([f"{i} min" for i in range(1, 1441)])
        self.distance_menu = self._make_simple_menu([f"{i/10:.1f} mi" for i in range(1, 10001)])
        self.incline_menu = self._make_simple_menu([f"{i}%" for i in range(0, 101)])

        # Root layout
        root = MDBoxLayout(orientation="vertical", spacing=dp(20), padding=dp(16))
        root.md_bg_color = self.BLACK

        scroll = MDScrollView(size_hint=(1, 1))
        vbox = MDBoxLayout(orientation="vertical", size_hint_y=None, height=0, spacing=dp(30))
        vbox.bind(minimum_height=vbox.setter("height"))
        scroll.add_widget(vbox)

        # All UI sections to render (exclude Equipment from sections; it's a per-row dropdown)
        categories_to_render = [
            "Strength Training",
            "Cardiovascular Training",
            "Recovery & Repair",
            "Flexibility and Mobility",
            "High-Intensity Interval Training",
            "Functional Training",
            "Group Fitness Classes",
            "Mind-Body Workouts",
        ]

        for section in categories_to_render:
            # Section header
            vbox.add_widget(self._section_header(section))

            # Container for multiple input rows
            container = MDBoxLayout(
                orientation="vertical",
                spacing=dp(12),
                size_hint_y=None,
                height=0,
                padding=(0, dp(6))
            )
            container.bind(minimum_height=container.setter("height"))

            # Starter rows per section
            for _ in range(2):
                container.add_widget(self._make_row(section, "Select Exercise", self.ALL_INPUTS))

            # "+ Add new exercise" link (adds another row)
            add_label = MDLabel(
                text="[u]+ Add new exercise[/u]",
                markup=True,
                theme_text_color="Custom",
                text_color=self.SILVER,
                halign="center",
                size_hint_y=None,
                height=dp(28)
            )
            add_label.bind(on_touch_down=lambda lbl, touch, sec=section, cont=container:
                           self._add_new_exercise(sec, cont) if lbl.collide_point(*touch.pos) else None)
            container.add_widget(add_label)

            setattr(self, f"{self._key(section)}_container", container)
            vbox.add_widget(container)

        # Footer
        footer = MDBoxLayout(size_hint_y=None, height=dp(56), padding=(dp(16), dp(10)), spacing=dp(12))
        footer.add_widget(Widget())
        back = MDLabel(text="[u]Return to Menu[/u]", markup=True,
                       theme_text_color="Custom", text_color=self.SILVER,
                       halign="right", valign="middle")
        back.bind(on_touch_down=self._on_return_to_menu)
        footer.add_widget(back)

        root.add_widget(scroll)
        root.add_widget(footer)
        self.add_widget(root)

    # ---------- Navigation ----------
    def _on_return_to_menu(self, lbl, touch):
        if lbl.collide_point(*touch.pos):
            self._call_app_menu()

    def _call_app_menu(self):
        app = self.get_app()
        if hasattr(app, "return_to_menu_dropdown"):
            try:
                app.return_to_menu_dropdown()
            except Exception:
                pass

    def get_app(self):
        from kivy.app import App
        return App.get_running_app()

    # ---------- UI helpers ----------
    def _section_header(self, title):
        return MDLabel(
            text=f"[u]{title}[/u]",
            markup=True,
            theme_text_color="Custom",
            text_color=self.SILVER,
            halign="left",
            size_hint_y=None,
            height=dp(28)
        )

    def _key(self, category):
        # Normalize keys so HIIT and special chars render reliably
        return (
            category.lower()
            .replace("&", "and")
            .replace("(", "")
            .replace(")", "")
            .replace("/", " ")
            .replace("-", " ")
            .replace("  ", " ")
            .replace(" ", "_")
        )

    def _outline_silver(self, tf):
        tf.line_color_normal = self.SILVER
        tf.line_color_focus = self.SILVER
        tf.text_color = self.WHITE
        tf.hint_text_color = (1, 1, 1, 0.7)
        tf.cursor_color = self.WHITE
        tf.foreground_color = self.WHITE

    # ---------- Stable menu open ----------
    def _open_menu(self, menu, caller):
        menu.caller = caller
        Clock.schedule_once(lambda *_: menu.open(), 0)

    # ---------- Dropdown menus ----------
    def _open_category_menu(self, category, caller):
        # Build/refresh menu on each open to include new user-added items
        names = self.exercises_by_category.get(category, []) + self.user_added_exercises.get(category, [])
        names = list(dict.fromkeys(names))
        names.append("+ Add new exercise…")

        items = []
        for name in names:
            items.append({
                "text": name,
                "theme_text_color": "Custom",
                "text_color": self.SILVER,
                "md_bg_color": self.BLACK,
                "height": dp(48),
                "on_release": lambda v=name, f=caller: self._apply_dropdown_choice(f, v)
            })

        key = self._key(category)
        menu = self.menus.get(key)
        if menu is None:
            menu = MDDropdownMenu(caller=caller, items=items, width=dp(300))
            try:
                menu.background_color = self.BLACK
                menu.width_mult = 4
            except Exception:
                pass
            self.menus[key] = menu
        else:
            menu.items = items
            menu.caller = caller

        self._active_menu = menu
        Clock.schedule_once(lambda *_: menu.open(), 0)

    def _open_equipment_menu(self, caller):
        base_list = self.exercises_by_category.get("Equipment", [])
        names = list(dict.fromkeys(base_list + self.user_added_equipment))
        names.append("+ Add new equipment…")

        items = []
        for name in names:
            items.append({
                "text": name,
                "theme_text_color": "Custom",
                "text_color": self.SILVER,
                "md_bg_color": self.BLACK,
                "height": dp(48),
                "on_release": lambda v=name, f=caller: self._apply_dropdown_choice(f, v)
            })

        key = "equipment_dropdown"
        menu = self.menus.get(key)
        if menu is None:
            menu = MDDropdownMenu(caller=caller, items=items, width=dp(300))
            try:
                menu.background_color = self.BLACK
                menu.width_mult = 4
            except Exception:
                pass
            self.menus[key] = menu
        else:
            menu.items = items
            menu.caller = caller

        self._active_menu = menu
        Clock.schedule_once(lambda *_: menu.open(), 0)

    def _apply_dropdown_choice(self, field, value):
        # Handle special actions first
        if value == "+ Add new exercise…":
            # Infer category from the label in the exercise pair
            try:
                ex_pair = field.parent          # vertical pair: field + label
                category_label = ex_pair.children[0]  # MDLabel under the field
                cat_text = category_label.text.replace("[u]", "").replace("[/u]", "")
                if cat_text in self.user_added_exercises:
                    new_name = f"Custom Exercise {len(self.user_added_exercises[cat_text]) + 1}"
                    self.user_added_exercises[cat_text].append(new_name)
                    field.text = new_name
            except Exception:
                pass
            if self._active_menu:
                try:
                    self._active_menu.dismiss()
                except Exception:
                    pass
            self._active_menu = None
            return

        if value == "+ Add new equipment…":
            new_eq = f"Custom Equipment {len(self.user_added_equipment) + 1}"
            self.user_added_equipment.append(new_eq)
            field.text = new_eq
            if self._active_menu:
                try:
                    self._active_menu.dismiss()
                except Exception:
                    pass
            self._active_menu = None
            return

        # Normal selection
        if field:
            field.text = value

        if self._active_menu:
            try:
                self._active_menu.dismiss()
            except Exception:
                pass
        self._active_menu = None

    def _make_simple_menu(self, values):
        # Create numeric menus with stable value capture
        menu = MDDropdownMenu(caller=None, items=[])
        try:
            menu.background_color = self.BLACK
            menu.width_mult = 4
        except Exception:
            pass
        items = []
        for val in values:
            items.append({
                "text": str(val),
                "theme_text_color": "Custom",
                "text_color": self.SILVER,
                "md_bg_color": self.BLACK,
                "height": dp(48),
                "on_release": lambda v=str(val), m=menu: self._apply_dropdown_choice(m.caller, v)
            })
        menu.items = items
        return menu

    # ---------- Row creation (exercise dropdown + six inputs + equipment) ----------
    def _make_row(self, category, exercise_name, inputs=None):
        row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(20),
            padding=(dp(10), dp(6)),
            size_hint_y=None,
            height=dp(84)
        )

        # Exercise selector (dropdown opens from the category label)
        label = MDLabel(
            text=f"[u]{category}[/u]",
            markup=True,
            theme_text_color="Custom",
            text_color=self.SILVER,
            halign="center",
            size_hint_x=None,
            width=dp(160)
        )

        field = MDTextField(
            text=exercise_name,
            readonly=True,
            size_hint_x=None,
            width=dp(320),
            foreground_color=self.WHITE,
            text_color=self.WHITE,
            hint_text_color=(1,1,1,0.7),
            cursor_color=self.WHITE,
            canvas_before=None
        )

        label.bind(on_touch_down=lambda lbl, touch, f=field: self._open_category_menu(category, f) if lbl.collide_point(*touch.pos) else None)

        row.add_widget(field)
        row.add_widget(label)

        # Six numeric inputs
        inputs_layout = MDBoxLayout(orientation="horizontal", spacing=dp(8))
        for i in range(3):
            tf = MDTextField(readonly=True, hint_text="", size_hint_x=None, width=dp(100), foreground_color=self.WHITE, text_color=self.WHITE)
            tf.canvas.before = None
            self._outline_silver(tf)
            inputs_layout.add_widget(tf)
        row.add_widget(inputs_layout)

        # equipment / accessory dropdown
        equip_field = MDTextField(readonly=True, hint_text="Equipment", size_hint_x=None, width=dp(160), foreground_color=self.WHITE, text_color=self.WHITE)
        equip_field.canvas.before = None
        self._outline_silver(equip_field)
        row.add_widget(equip_field)

        equip_label = MDLabel(text="[u]Equipment[/u]", markup=True, theme_text_color="Custom", text_color=self.SILVER, halign="center", size_hint_x=None, width=dp(120))
        equip_label.bind(on_touch_down=lambda lbl, touch, f=equip_field: self._open_equipment_menu(f) if lbl.collide_point(*touch.pos) else None)
        row.add_widget(equip_label)

        return row

# ----------------------------
# App class
# ----------------------------
class DelphiaFitnessTrackerApp(MDApp):
    # Colors
    primary_color = ListProperty([0.129, 0.588, 0.953, 1])
    protein_color = ListProperty([1, 0.2, 0.2, 1])
    water_color = ListProperty([0.2, 0, 1, 1])
    calories_color = ListProperty([0.2, 0.8, 0.2, 1])
    profile_color = ListProperty([0.6, 0.2, 0.8, 1])
    meals_color = ListProperty([1, 0.5, 0, 1])

    # Profile data
    name = StringProperty("")
    dob = StringProperty("")
    gender = StringProperty("male")

    # Units
    weight_unit = StringProperty("kg")
    height_unit = StringProperty("cm")

    # Weights
    starting_weight = NumericProperty(0.0)
    total_weight = NumericProperty(0.0)
    total_weight_color = ListProperty([1, 1, 0, 1])
    total_change_text = StringProperty("—")

    # Height / BMI
    height_m = NumericProperty(0.0)
    height_value = NumericProperty(0.0)
    bmi = NumericProperty(0.0)
    bmi_category = StringProperty("")
    bmi_text = StringProperty("—")

    # Intakes
    protein_intake = NumericProperty(0.0)
    water_intake = NumericProperty(0.0)
    calorie_intake = NumericProperty(0.0)

    # Daily goals
    protein_goal = NumericProperty(0.0)
    water_goal = NumericProperty(0.0)
    calorie_goal = NumericProperty(0.0)

    # Calorie targets used in KV
    calorie_target_male = NumericProperty(0.0)
    calorie_target_female = NumericProperty(0.0)

    # Goals
    target_weight = NumericProperty(0.0)
    weekly_weight_change_goal = NumericProperty(0.0)
    goal_streak_days = NumericProperty(0)
    goal_deadline = StringProperty("")
    goal_note = StringProperty("")
    custom_goal = StringProperty("")
    mood_goal = StringProperty("")
    habits = StringProperty("")
    remind_weekly = BooleanProperty(False)
    goals_visibility = StringProperty("")
    stress_level = StringProperty("")
    mindfulness_type = StringProperty("")
    mental_reset_action = StringProperty("")

    # Text input mirrors used in KV
    starting_weight_input = StringProperty("")
    total_weight_input = StringProperty("")
    target_weight_input = StringProperty("")
    weekly_change_input = StringProperty("")

    # Files
    PROFILE_FILE = Path("profile.json")
    COMMUNITY_FILE = Path("community.json")

    # UI state
    _menu = None

    # Lifecycle
    def build(self):
        # Use in-memory settings (no file-based JsonStore) — persistence is handled by backend
        self.settings = {}
        self.target_weight = self.settings.get("target_weight", 0)
        return Builder.load_file(str(Path(__file__).parent / "main.kv"))

    def on_start(self):
        try:
            sm = self.root
            expected = {
                "home": HomeScreen,
                "protein": ProteinScreen,
                "water": WaterScreen,
                "calories": CaloriesScreen,
                "meals": MealsScreen,
                "workouts": WorkoutsScreen,
                "profile": ProfileScreen,
                "goals": GoalsScreen,
                "community": CommunityScreen,
                "supplements": SupplementsScreen,
                "sports": SportsScreen,
                "freetraining": FreeTrainingScreen,
            }
            loaded = {s.name: s for s in sm.screens if getattr(s, "name", "")}
            print("Screens loaded:", list(loaded.keys()))
            print("Current screen:", sm.current)
            for name, cls in expected.items():
                if name not in loaded and cls is not None:
                    sm.add_widget(cls(name=name))
                elif name in loaded and not loaded[name].name:
                    loaded[name].name = name
        except Exception as e:
            print("on_start error:", e)

    # Navigation menu
    def _menu_items(self):
        entries = [
            ("Home", "home"), ("Protein", "protein"), ("Water", "water"),
            ("Calories", "calories"), ("Meals", "meals"), ("Workouts", "workouts"),
            ("Profile", "profile"), ("Goals", "goals"), ("Community", "community"),
            ("Supplements", "supplements"), ("Sports", "sports"), ("FreeTraining", "freetraining")
        ]
        return [{"text": label, "on_release": self._make_switch_callback(target)} for label, target in entries]

    def _make_switch_callback(self, target):
        return lambda *args: self._switch_screen(target)

    def _resolve_menu_caller(self, caller):
        try:
            from kivy.uix.screenmanager import Screen as KivyScreen
            if caller is not None and not isinstance(caller, KivyScreen):
                return caller
            screen = getattr(self.root, "current_screen", None)
            if not screen:
                return caller
            if hasattr(screen, "ids") and "menu_btn" in screen.ids:
                return screen.ids.menu_btn
            if not hasattr(screen, "_menu_anchor_overlay"):
                overlay = FloatLayout(size_hint=(1, 1))
                screen.add_widget(overlay)
                screen._menu_anchor_overlay = overlay
            if not hasattr(screen, "_menu_anchor"):
                anchor = Widget(size_hint=(None, None), size=(1, 1))
                anchor.pos_hint = {"x": 0, "top": 1}
                screen._menu_anchor_overlay.add_widget(anchor)
                screen._menu_anchor = anchor
            return screen._menu_anchor
        except Exception:
            return caller

    def return_to_menu_dropdown(self, caller=None):
        try:
            if getattr(self, "_menu", None):
                self._menu.dismiss()
                self._menu = None
            anchor = self._resolve_menu_caller(caller)
            self._menu = MDDropdownMenu(caller=anchor, items=self._menu_items(), width_mult=3)
            self._menu.open()
        except Exception as e:
            print("return_to_menu_dropdown error:", e)

    def _switch_screen(self, screen_name):
        try:
            if getattr(self, "_menu", None):
                self._menu.dismiss()
                self._menu = None
            self.root.current = screen_name
        except Exception as e:
            print(f"Error switching to '{screen_name}':", e)

    def toggle_menu(self, caller=None):
        self.return_to_menu_dropdown(caller)

    # Profile / BMI helpers
    def _on_starting_weight_text(self, text):
        try:
            self.starting_weight_input = text or ""
            self.starting_weight = float(text) if text not in (None, "", "-") else 0.0
        except Exception:
            self.starting_weight = 0.0
        self._update_total_change_text()
        self._update_bmi()

    def _on_total_weight_text(self, text):
        try:
            self.total_weight_input = text or ""
            self.total_weight = float(text) if text not in (None, "", "-") else 0.0
        except Exception:
            self.total_weight = 0.0
        self._update_total_weight_color()
        self._update_total_change_text()
        self._update_bmi()

    def _on_height_text(self, text):
        try:
            v = float(text) if text not in (None, "", "-") else 0.0
            self.height_value = v
            unit = getattr(self, "height_unit", "cm")
            if unit == "cm":
                self.height_m = v / 100.0
            else:
                self.height_m = (v * 2.54) / 100.0
        except Exception:
            self.height_m = 0.0
        self._update_bmi()

    def _update_total_change_text(self):
        try:
            start = getattr(self, "starting_weight", 0.0)
            total = getattr(self, "total_weight", 0.0)
            change = total - start
            self.total_change_text = f"{change:+.1f}"
        except Exception:
            self.total_change_text = "—"

    def _update_total_weight_color(self):
        try:
            start = getattr(self, "starting_weight", 0.0)
            total = getattr(self, "total_weight", 0.0)
            change = total - start
            if change < 0:
                self.total_weight_color = [0, 1, 0, 1]
            elif change > 0:
                self.total_weight_color = [1, 0, 0, 1]
            else:
                self.total_weight_color = [1, 1, 0, 1]
        except Exception:
            self.total_weight_color = [1, 1, 0, 1]

    def _update_bmi(self):
        try:
            total = getattr(self, "total_weight", 0.0)
            h_m = getattr(self, "height_m", 0.0)
            if h_m > 0:
                self.bmi = total / (h_m ** 2)
                self.bmi_text = f"{self.bmi:.1f}"
                bmi = self.bmi
                if bmi < 18.5:
                    self.bmi_category = "Underweight"
                elif bmi < 25:
                    self.bmi_category = "Normal"
                elif bmi < 30:
                    self.bmi_category = "Overweight"
                else:
                    self.bmi_category = "Obese"
            else:
                self.bmi_text = "—"
                self.bmi_category = ""
        except Exception:
            self.bmi_text = "—"
            self.bmi_category = ""

    # Goals / parsing hooks
    def set_target_weight_from_text(self, text):
        try:
            value = float(text) if text not in (None, "", "-") else 0.0
            self.target_weight_input = text or ""
            self.target_weight = int(value) if float(value).is_integer() else value
        except Exception:
            self.target_weight = 0
        try:
            # Keep in in-memory settings until backend persistence is wired
            self.settings["target_weight"] = self.target_weight
        except Exception:
            pass

    def _on_target_weight_text(self, text):
        self.set_target_weight_from_text(text)

    # Avatar/profile stubs
    def open_file_chooser(self):
        print("open_file_chooser: not implemented")

    def set_avatar_from_camera(self):
        print("set_avatar_from_camera: not implemented")

    def clear_avatar(self):
        try:
            self.avatar_path = ""
            self.initials = ""
            print("Avatar cleared.")
        except Exception:
            pass

    def save_profile(self):
        try:
            data = {
                "name": self.name,
                "dob": self.dob,
                "gender": self.gender,
                "weight_unit": self.weight_unit,
                "height_unit": self.height_unit,
                "starting_weight": self.starting_weight,
                "total_weight": self.total_weight,
                "height_value": self.height_value,
                "avatar_path": getattr(self, "avatar_path", ""),
                "initials": getattr(self, "initials", ""),
            }
            with self.PROFILE_FILE.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print("Profile saved.")
        except Exception as e:
            print("Failed to save profile:", e)

# ----------------------------
# Run the app
# ----------------------------
if __name__ == "__main__":
    DelphiaFitnessTrackerApp().run()
