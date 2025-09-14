import tkinter as tk
from tkinter import ttk, messagebox
import requests
import aiohttp
import asyncio
import threading
import time
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from io import BytesIO

class WeatherComparisonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Weather Comparison Tool")
        self.root.geometry("1200x600")
        
        # Configuration
        self.API_KEY = "09e8d91f67b55d144924ef2e64e6d593"  # Replace with your OpenWeatherMap API key
        self.WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
        self.DEFAULT_CITIES = ["London", "Paris", "Tokyo", "New York", "Sydney"]
        
        # Data storage
        self.sync_times = []
        self.async_times = []
        self.sync_success = 0
        self.async_success = 0
        self.request_history = []
        
        # UI Setup
        self.create_menu_bar()
        self.create_home_page()
        self.create_status_bar()
        
        # Load default icon
        self.load_default_icon()

    def load_default_icon(self):
        try:
            # Try to load a default weather icon
            self.weather_icon = Image.open("weather_icon.png")
            self.weather_icon = self.weather_icon.resize((150, 150), Image.LANCZOS)
            # self.tk_weather_icon = ImageTk.PhotoImage(self.weather_icon)
        except:
            pass
            # self.tk_weather_icon = None

    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Home", command=self.create_home_page)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Request menu
        request_menu = tk.Menu(menubar, tearoff=0)
        request_menu.add_command(label="Single City Test", command=self.create_single_city_page)
        request_menu.add_command(label="Batch City Test", command=self.create_batch_city_page)
        menubar.add_cascade(label="Requests", menu=request_menu)
        
        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        analysis_menu.add_command(label="Performance Graphs", command=self.show_performance_graphs)
        analysis_menu.add_command(label="Request Timeline", command=self.show_request_timeline)
        analysis_menu.add_command(label="Statistics Dashboard", command=self.show_stats_dashboard)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        
        # Test menu
        test_menu = tk.Menu(menubar, tearoff=0)
        test_menu.add_command(label="UI Responsiveness", command=self.test_ui_responsiveness)
        test_menu.add_command(label="Concurrency Test", command=self.test_concurrency_limits)
        menubar.add_cascade(label="Tests", menu=test_menu)
        
        self.root.config(menu=menubar)

    def create_status_bar(self):
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, 
                 relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X)

    def create_home_page(self):
        self.clear_frame()
        
        # Header frame
        header_frame = ttk.Frame(self.root, padding="20")
        header_frame.pack(fill=tk.X)
        
        # if self.tk_weather_icon:
        #     ttk.Label(header_frame, image=self.tk_weather_icon).pack(side=tk.LEFT, padx=10)
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        ttk.Label(title_frame, text="Weather API Comparison Tool", 
                 font=('Helvetica', 18, 'bold')).pack(anchor=tk.W)
        ttk.Label(title_frame, text="Compare synchronous vs asynchronous API requests", 
                 font=('Helvetica', 12)).pack(anchor=tk.W)
        
        # Features frame
        features_frame = ttk.Frame(self.root, padding="20")
        features_frame.pack(fill=tk.BOTH, expand=True)
        
        features = [
            "• Single city weather fetching (sync/async)",
            "• Batch city weather data collection",
            "• Performance comparison graphs",
            "• Request timeline visualization",
            "• Detailed statistics dashboard",
            "• UI responsiveness testing",
            "• Concurrency limit testing"
        ]
        
        for feature in features:
            ttk.Label(features_frame, text=feature, font=('Helvetica', 11)).pack(anchor=tk.W, pady=2)
        
        '''# Quick start frame
        quick_frame = ttk.LabelFrame(self.root, text="Quick Start", padding="15")
        quick_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(quick_frame, text="Enter city:").pack(side=tk.LEFT)
        self.quick_city_entry = ttk.Entry(quick_frame, width=20)
        self.quick_city_entry.pack(side=tk.LEFT, padx=5)
        self.quick_city_entry.insert(0, "London")
        
        ttk.Button(quick_frame, text="Test Sync", 
                  command=lambda: self.fetch_weather_sync(self.quick_city_entry.get())).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="Test Async", 
                  command=lambda: self.fetch_weather_async(self.quick_city_entry.get())).pack(side=tk.LEFT, padx=5)
		'''

    def create_single_city_page(self):
        self.clear_frame()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Input frame
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="City:").pack(side=tk.LEFT)
        self.city_entry = ttk.Entry(input_frame, width=25)
        self.city_entry.pack(side=tk.LEFT, padx=5)
        self.city_entry.insert(0, "London")
        
        ttk.Button(input_frame, text="Fetch Synchronously", 
                  command=lambda: self.fetch_weather_sync(self.city_entry.get())).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Fetch Asynchronously", 
                  command=lambda: self.fetch_weather_async(self.city_entry.get())).pack(side=tk.LEFT, padx=5)
        
        # Results frame
        results_frame = ttk.Frame(frame)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sync results
        sync_frame = ttk.LabelFrame(results_frame, text="Synchronous Results", padding="10")
        sync_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.sync_text = tk.Text(sync_frame, height=15, state=tk.DISABLED, wrap=tk.WORD)
        self.sync_text.pack(fill=tk.BOTH, expand=True)
        
        # Async results
        async_frame = ttk.LabelFrame(results_frame, text="Asynchronous Results", padding="10")
        async_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.async_text = tk.Text(async_frame, height=15, state=tk.DISABLED, wrap=tk.WORD)
        self.async_text.pack(fill=tk.BOTH, expand=True)
        
        # Back button
        ttk.Button(frame, text="Back to Home", command=self.create_home_page).pack(pady=10)

    def create_batch_city_page(self):
        self.clear_frame()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Input frame
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="Cities (comma separated):").pack(side=tk.LEFT)
        self.cities_entry = ttk.Entry(input_frame, width=50)
        self.cities_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.cities_entry.insert(0, ", ".join(self.DEFAULT_CITIES))
        
        # Button frame
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Fetch All Synchronously", 
                  command=lambda: self.batch_fetch(sync=True)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Fetch All Asynchronously", 
                  command=lambda: self.batch_fetch(sync=False)).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, pady=10)
        
        # Results treeview
        self.results_tree = ttk.Treeview(frame, columns=('City', 'Temp', 'Weather', 'Time', 'Method'), show='headings')
        self.results_tree.heading('City', text='City')
        self.results_tree.heading('Temp', text='Temp (°C)')
        self.results_tree.heading('Weather', text='Weather')
        self.results_tree.heading('Time', text='Time (s)')
        self.results_tree.heading('Method', text='Method')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscroll=scrollbar.set)
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Back button
        ttk.Button(frame, text="Back to Home", command=self.create_home_page).pack(pady=10)

    def fetch_weather_sync(self, city):
        if not city:
            messagebox.showerror("Error", "Please enter a city name")
            return
        
        self.status_var.set(f"Fetching weather for {city} (Synchronous)...")
        self.root.update()
        
        start_time = time.time()
        
        try:
            response = requests.get(
                self.WEATHER_URL,
                params={"q": city, "appid": self.API_KEY, "units": "metric"},
                timeout=10
            )
            data = response.json()
            
            if response.status_code != 200:
                self.update_results(self.sync_text, f"Error: {data.get('message', 'Unknown error')}")
                return
                
            elapsed = time.time() - start_time
            self.sync_times.append(elapsed)
            self.sync_success += 1
            self.request_history.append(("sync", city, elapsed))
            
            result_text = (
                f"City: {city}\n"
                f"Temperature: {data['main']['temp']}°C\n"
                f"Weather: {data['weather'][0]['description'].title()}\n"
                f"Humidity: {data['main']['humidity']}%\n"
                f"Wind: {data['wind']['speed']} m/s\n"
                f"Time taken: {elapsed:.3f} seconds\n"
				f"---------------------------------------------\n"
            )
            
            self.update_results(self.sync_text, result_text)
            
        except Exception as e:
            self.update_results(self.sync_text, f"Error: {str(e)}")
        finally:
            self.status_var.set(f"Completed synchronous request for {city}")

    def fetch_weather_async(self, city):
        if not city:
            messagebox.showerror("Error", "Please enter a city name")
            return
        
        self.status_var.set(f"Fetching weather for {city} (Asynchronous)...")
        
        threading.Thread(
            target=self.run_async_fetch,
            args=(city,),
            daemon=True
        ).start()

    def run_async_fetch(self, city):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.async_fetch_weather(city))
        finally:
            loop.close()

    async def async_fetch_weather(self, city):
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.WEATHER_URL,
                    params={"q": city, "appid": self.API_KEY, "units": "metric"},
                    timeout=10
                ) as response:
                    data = await response.json()
                    
                    if response.status != 200:
                        self.root.after(0, self.update_results,
                                      self.async_text,
                                      f"Error: {data.get('message', 'Unknown error')}")
                        return
                        
                    elapsed = time.time() - start_time
                    self.async_times.append(elapsed)
                    self.async_success += 1
                    self.request_history.append(("async", city, elapsed))
                    
                    result_text = (
                        f"City: {city}\n"
                        f"Temperature: {data['main']['temp']}°C\n"
                        f"Weather: {data['weather'][0]['description'].title()}\n"
                        f"Humidity: {data['main']['humidity']}%\n"
                        f"Wind: {data['wind']['speed']} m/s\n"
                        f"Time taken: {elapsed:.3f} seconds\n"
						f"-------------------------------------\n"
                    )
                    
                    self.root.after(0, self.update_results,
                                  self.async_text,
                                  result_text)
                    
        except Exception as e:
            self.root.after(0, self.update_results,
                          self.async_text,
                          f"Error: {str(e)}")
        finally:
            self.root.after(0, lambda: self.status_var.set(f"Completed async request for {city}"))

    def batch_fetch(self, sync=True):
        cities = [city.strip() for city in self.cities_entry.get().split(",") if city.strip()]
        if not cities:
            messagebox.showerror("Error", "Please enter at least one city")
            return
        
        self.progress["maximum"] = len(cities)
        self.progress["value"] = 0
        
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        if sync:
            self.run_sync_batch(cities)
        else:
            threading.Thread(target=self.run_async_batch, args=(cities,), daemon=True).start()

    def run_sync_batch(self, cities):
        total_start = time.time()
        
        for i, city in enumerate(cities, 1):
            start_time = time.time()
            try:
                response = requests.get(
                    self.WEATHER_URL,
                    params={"q": city, "appid": self.API_KEY, "units": "metric"},
                    timeout=10
                )
                data = response.json()
                
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    self.sync_times.append(elapsed)
                    self.sync_success += 1
                    self.request_history.append(("sync", city, elapsed))
                    
                    self.root.after(0, self.add_to_results_tree,
                                   (city, data['main']['temp'], 
                                    data['weather'][0]['description'].title(),
                                    f"{elapsed:.3f}", "Sync"))
                else:
                    self.root.after(0, self.add_to_results_tree,
                                   (city, "N/A", data.get('message', 'Error'), 
                                    f"{elapsed:.3f}", "Sync (Failed)"))
                
            except Exception as e:
                elapsed = time.time() - start_time
                self.root.after(0, self.add_to_results_tree,
                               (city, "N/A", str(e), f"{elapsed:.3f}", "Sync (Failed)"))
            
            self.root.after(0, lambda i=i: self.progress.config(value=i))
            self.root.after(0, lambda: self.status_var.set(
                f"Processed {i}/{len(cities)} cities synchronously"))
        
        total_elapsed = time.time() - total_start
        self.root.after(0, lambda: self.status_var.set(
            f"Completed batch sync for {len(cities)} cities in {total_elapsed:.2f} seconds"))

    def run_async_batch(self, cities):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.async_batch_fetch(cities))
        finally:
            loop.close()

    async def async_batch_fetch(self, cities):
        total_start = time.time()
        tasks = []
        
        async with aiohttp.ClientSession() as session:
            for i, city in enumerate(cities, 1):
                task = asyncio.create_task(self.async_fetch_city(session, city, i, len(cities)))
                tasks.append(task)
            
            await asyncio.gather(*tasks)
        
        total_elapsed = time.time() - total_start
        self.root.after(0, lambda: self.status_var.set(
            f"Completed batch async for {len(cities)} cities in {total_elapsed:.2f} seconds"))

    async def async_fetch_city(self, session, city, current, total):
        start_time = time.time()
        
        try:
            async with session.get(
                self.WEATHER_URL,
                params={"q": city, "appid": self.API_KEY, "units": "metric"},
                timeout=10
            ) as response:
                data = await response.json()
                elapsed = time.time() - start_time
                
                if response.status == 200:
                    self.async_times.append(elapsed)
                    self.async_success += 1
                    self.request_history.append(("async", city, elapsed))
                    
                    self.root.after(0, self.add_to_results_tree,
                                  (city, data['main']['temp'], 
                                   data['weather'][0]['description'].title(),
                                   f"{elapsed:.3f}", "Async"))
                else:
                    self.root.after(0, self.add_to_results_tree,
                                  (city, "N/A", data.get('message', 'Error'), 
                                   f"{elapsed:.3f}", "Async (Failed)"))
                
        except Exception as e:
            elapsed = time.time() - start_time
            self.root.after(0, self.add_to_results_tree,
                          (city, "N/A", str(e), f"{elapsed:.3f}", "Async (Failed)"))
        
        self.root.after(0, lambda i=current: self.progress.config(value=i))
        self.root.after(0, lambda: self.status_var.set(
            f"Processed {current}/{total} cities asynchronously"))

    def add_to_results_tree(self, values):
        self.results_tree.insert('', tk.END, values=values)
        self.results_tree.yview_moveto(1)  # Auto-scroll to bottom

    def show_performance_graphs(self):
        self.clear_frame()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        if not self.sync_times and not self.async_times:
            ttk.Label(frame, text="No performance data available yet. Make some requests first.").pack(pady=20)
            ttk.Button(frame, text="Back to Home", command=self.create_home_page).pack(pady=10)
            return
        
        # Create matplotlib figure
        fig = Figure(figsize=(10, 5), dpi=100)
        plot = fig.add_subplot(111)
        
        if self.sync_times:
            plot.plot(range(1, len(self.sync_times)+1), self.sync_times, 'r-', label='Synchronous', marker='o')
        if self.async_times:
            plot.plot(range(1, len(self.async_times)+1), self.async_times, 'b-', label='Asynchronous', marker='o')
        
        plot.set_title('Request Performance Comparison')
        plot.set_xlabel('Request Number')
        plot.set_ylabel('Time Taken (seconds)')
        plot.legend()
        plot.grid(True)
        
        # Embed plot in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add stats
        stats_frame = ttk.Frame(frame)
        stats_frame.pack(pady=10)
        
        if self.sync_times:
            ttk.Label(stats_frame, 
                     text=f"Sync Avg: {np.mean(self.sync_times):.3f}s | "
                          f"Min: {min(self.sync_times):.3f}s | "
                          f"Max: {max(self.sync_times):.3f}s | "
                          f"Total: {sum(self.sync_times):.2f}s").pack()
        
        if self.async_times:
            ttk.Label(stats_frame, 
                     text=f"Async Avg: {np.mean(self.async_times):.3f}s | "
                          f"Min: {min(self.async_times):.3f}s | "
                          f"Max: {max(self.async_times):.3f}s | "
                          f"Total: {sum(self.async_times):.2f}s").pack()
        
        ttk.Button(frame, text="Back to Home", command=self.create_home_page).pack(pady=10)

    def show_request_timeline(self):
        self.clear_frame()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        if not self.request_history:
            ttk.Label(frame, text="No request history available yet. Make some requests first.").pack(pady=20)
            ttk.Button(frame, text="Back to Home", command=self.create_home_page).pack(pady=10)
            return
        
        # Create matplotlib figure
        fig = Figure(figsize=(10, 6), dpi=100)
        plot = fig.add_subplot(111)
        
        # Prepare data for timeline
        sync_times = []
        async_times = []
        
        for i, (method, city, elapsed) in enumerate(self.request_history):
            if method == "sync":
                sync_times.append((i, elapsed, city))
            else:
                async_times.append((i, elapsed, city))
        
        if sync_times:
            x, y, labels = zip(*sync_times)
            plot.scatter(x, y, c='red', label='Synchronous', s=100)
            for i, (xi, yi, label) in enumerate(zip(x, y, labels)):
                plot.text(xi, yi, f" {label}", fontsize=8, va='center')
        
        if async_times:
            x, y, labels = zip(*async_times)
            plot.scatter(x, y, c='blue', label='Asynchronous', s=100)
            for i, (xi, yi, label) in enumerate(zip(x, y, labels)):
                plot.text(xi, yi, f" {label}", fontsize=8, va='center')
        
        plot.set_title('Request Timeline Visualization')
        plot.set_xlabel('Request Sequence')
        plot.set_ylabel('Time Taken (seconds)')
        plot.legend()
        plot.grid(True)
        
        # Embed plot in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(frame, text="Back to Home", command=self.create_home_page).pack(pady=10)

    def show_stats_dashboard(self):
        self.clear_frame()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create dashboard frames
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill=tk.X, pady=10)
        
        # Summary stats
        summary_frame = ttk.LabelFrame(top_frame, text="Summary Statistics", padding="10")
        summary_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        stats = [
            ("Total Requests", len(self.request_history)),
            ("Sync Requests", len(self.sync_times)),
            ("Async Requests", len(self.async_times)),
            ("Sync Success Rate", f"{self.sync_success/len(self.sync_times)*100:.1f}%" if self.sync_times else "N/A"),
            ("Async Success Rate", f"{self.async_success/len(self.async_times)*100:.1f}%" if self.async_times else "N/A"),
            ("Fastest Request", f"{min(self.sync_times + self.async_times):.3f}s" if self.request_history else "N/A"),
            ("Slowest Request", f"{max(self.sync_times + self.async_times):.3f}s" if self.request_history else "N/A")
        ]
        
        for i, (label, value) in enumerate(stats):
            ttk.Label(summary_frame, text=label, font=('Helvetica', 10, 'bold')).grid(row=i, column=0, sticky=tk.W, pady=2)
            ttk.Label(summary_frame, text=value).grid(row=i, column=1, sticky=tk.W, pady=2)
        
        # Recent requests
        recent_frame = ttk.LabelFrame(top_frame, text="Recent Requests", padding="10")
        recent_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        recent_tree = ttk.Treeview(recent_frame, columns=('Method', 'City', 'Time'), show='headings', height=5)
        recent_tree.heading('Method', text='Method')
        recent_tree.heading('City', text='City')
        recent_tree.heading('Time', text='Time (s)')
        
        for item in recent_tree.get_children():
            recent_tree.delete(item)
        
        for req in self.request_history[-10:]:  # Show last 10 requests
            recent_tree.insert('', tk.END, values=(req[0].title(), req[1], f"{req[2]:.3f}"))
        
        recent_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bottom frame for charts
        bottom_frame = ttk.Frame(frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Small charts
        if self.sync_times and self.async_times:
            fig = Figure(figsize=(10, 4), dpi=80)
            
            # Avg time comparison
            ax1 = fig.add_subplot(121)
            methods = ['Sync', 'Async']
            averages = [np.mean(self.sync_times), np.mean(self.async_times)]
            ax1.bar(methods, averages, color=['red', 'blue'])
            ax1.set_title('Average Response Time')
            ax1.set_ylabel('Seconds')
            
            # Success rate comparison
            ax2 = fig.add_subplot(122)
            success_rates = [
                self.sync_success/len(self.sync_times)*100,
                self.async_success/len(self.async_times)*100
            ]
            ax2.bar(methods, success_rates, color=['red', 'blue'])
            ax2.set_title('Success Rate Comparison')
            ax2.set_ylabel('Percentage (%)')
            ax2.set_ylim(0, 100)
            
            canvas = FigureCanvasTkAgg(fig, master=bottom_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(frame, text="Back to Home", command=self.create_home_page).pack(pady=10)

    def test_ui_responsiveness(self):
        self.clear_frame()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        self.test_label = ttk.Label(frame, text="UI Responsiveness Test", font=('Helvetica', 14))
        self.test_label.pack(pady=10)
        
        self.counter = 0
        self.counter_label = ttk.Label(frame, text=f"Counter: {self.counter}", font=('Helvetica', 12))
        self.counter_label.pack(pady=10)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Start Counter", command=self.start_counter).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Fetch Sync During Test", 
                  command=lambda: self.fetch_during_test(sync=True)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Fetch Async During Test", 
                  command=lambda: self.fetch_during_test(sync=False)).pack(side=tk.LEFT, padx=5)
        
        self.test_text = tk.Text(frame, height=10, state=tk.DISABLED)
        self.test_text.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(frame, text="Back to Home", command=self.create_home_page).pack(pady=10)

    def start_counter(self):
        self.counter = 0
        self.update_counter()

    def update_counter(self):
        self.counter += 1
        self.counter_label.config(text=f"Counter: {self.counter}")
        if self.counter < 50:  # Count up to 50
            self.root.after(100, self.update_counter)  # Update every 100ms

    def fetch_during_test(self, sync=True):
        city = "London"  # Default city for test
        if sync:
            self.fetch_weather_sync(city)
        else:
            self.fetch_weather_async(city)

    def test_concurrency_limits(self):
        self.clear_frame()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Concurrency Limit Test", font=('Helvetica', 14)).pack(pady=10)
        
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="Number of concurrent requests:").pack(side=tk.LEFT)
        self.concurrency_var = tk.IntVar(value=10)
        ttk.Entry(input_frame, textvariable=self.concurrency_var, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(input_frame, text="Run Test", command=self.run_concurrency_test).pack(side=tk.LEFT, padx=10)
        
        self.concurrency_text = tk.Text(frame, height=15, state=tk.DISABLED)
        self.concurrency_text.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(frame, text="Back to Home", command=self.create_home_page).pack(pady=10)

    def run_concurrency_test(self):
        num_requests = self.concurrency_var.get()
        if num_requests < 1:
            messagebox.showerror("Error", "Number of requests must be at least 1")
            return
        
        self.update_results(self.concurrency_text, f"Starting concurrency test with {num_requests} async requests...\n")
        
        threading.Thread(
            target=self.execute_concurrency_test,
            args=(num_requests,),
            daemon=True
        ).start()

    def execute_concurrency_test(self, num_requests):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.run_async_concurrency_test(num_requests))
        finally:
            loop.close()

    async def run_async_concurrency_test(self, num_requests):
        cities = [f"TestCity{i}" for i in range(1, num_requests+1)]
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for city in cities:
                task = asyncio.create_task(self.test_async_request(session, city))
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.time() - start_time
        
        success = sum(1 for r in results if not isinstance(r, Exception))
        
        self.root.after(0, self.update_results,
                      self.concurrency_text,
                      f"\nCompleted {num_requests} async requests in {elapsed:.2f} seconds\n"
                      f"Success rate: {success}/{num_requests} ({success/num_requests*100:.1f}%)\n"
                      f"Average time per request: {elapsed/num_requests:.3f}s\n")

    async def test_async_request(self, session, city):
        try:
            start_time = time.time()
            async with session.get(
                self.WEATHER_URL,
                params={"q": city, "appid": self.API_KEY, "units": "metric"},
                timeout=10
            ) as response:
                await response.json()
                elapsed = time.time() - start_time
                
                self.root.after(0, self.update_results,
                              self.concurrency_text,
                              f"Request for {city}: {response.status} in {elapsed:.3f}s\n")
                
                if response.status == 200:
                    return True
                return False
                
        except Exception as e:
            self.root.after(0, self.update_results,
                          self.concurrency_text,
                          f"Request for {city} failed: {str(e)}\n")
            raise e

    def update_results(self, text_widget, content):
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, content)
        text_widget.see(tk.END)
        text_widget.config(state=tk.DISABLED)

    def clear_frame(self):
        for widget in self.root.winfo_children():
            if not isinstance(widget, tk.Menu) and not isinstance(widget, ttk.Label):
                widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherComparisonApp(root)
    root.mainloop()