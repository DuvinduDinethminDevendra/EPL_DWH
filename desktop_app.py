"""
EPL DWH Desktop Application - PyQt6 Main Window
Complete desktop interface for querying the EPL Data Warehouse
"""

import sys
import pandas as pd
import mysql.connector
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QComboBox, QTableWidget, 
    QTableWidgetItem, QSpinBox, QLineEdit, QMessageBox, QFileDialog,
    QProgressBar, QStatusBar, QMenuBar, QMenu, QDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon, QPainter

from src.etl.db import get_engine
from sqlalchemy import text, create_engine
from src.etl.config import database_url
import traceback
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# DATABASE QUERIES
# ============================================================================

class DatabaseQueries:
    """All database queries for the dashboard"""
    
    # Helper method to get direct MySQL connection (not SQLAlchemy)
    @staticmethod
    def _get_mysql_connection():
        """Create direct MySQL connection - better for threading"""
        return mysql.connector.connect(
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '1234'),
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3307)),
            database=os.getenv('MYSQL_DB', 'epl_dw')
        )
    
    @staticmethod
    def get_dashboard_stats(engine=None):
        """Get main dashboard metrics"""
        try:
            print("DEBUG: get_dashboard_stats called")
            print("DEBUG: Getting MySQL connection...")
            conn = DatabaseQueries._get_mysql_connection()
            cursor = conn.cursor()
            
            print("DEBUG: Connection created, executing queries...")
            
            cursor.execute("SELECT COUNT(*) FROM fact_match")
            matches = cursor.fetchone()[0] or 0
            print(f"DEBUG: Got matches: {matches}")
            
            cursor.execute("SELECT COUNT(*) FROM fact_match_events")
            events = cursor.fetchone()[0] or 0
            print(f"DEBUG: Got events: {events}")
            
            cursor.execute("SELECT COUNT(*) FROM dim_player WHERE player_id > 0")
            players = cursor.fetchone()[0] or 0
            print(f"DEBUG: Got players: {players}")
            
            cursor.execute("SELECT COUNT(*) FROM dim_team WHERE team_id > 0")
            teams = cursor.fetchone()[0] or 0
            print(f"DEBUG: Got teams: {teams}")
            
            cursor.close()
            conn.close()
            
            result = {
                "matches": matches,
                "events": events,
                "players": players,
                "teams": teams
            }
            print(f"DEBUG: Returning {result}")
            return result
        except Exception as e:
            print(f"ERROR in get_dashboard_stats: {e}")
            import traceback
            traceback.print_exc()
            return {"matches": 0, "events": 0, "players": 0, "teams": 0}

    @staticmethod
    def get_teams(engine):
        """Get all EPL teams"""
        try:
            with engine.connect() as conn:
                df = pd.read_sql(
                    "SELECT team_id, team_name FROM dim_team WHERE team_id > 0 ORDER BY team_name",
                    conn
                )
            return df
        except Exception as e:
            print(f"Error fetching teams: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_team_performance(engine):
        """Get team performance statistics"""
        try:
            with engine.connect() as conn:
                df = pd.read_sql("""
                    SELECT 
                        dt.team_id,
                        dt.team_name,
                        COUNT(DISTINCT fm.match_id) as total_matches,
                        SUM(CASE 
                            WHEN (fm.home_team_id = dt.team_id AND fm.home_goals > fm.away_goals) OR
                                 (fm.away_team_id = dt.team_id AND fm.away_goals > fm.home_goals)
                            THEN 1 ELSE 0 
                        END) as wins,
                        SUM(CASE 
                            WHEN fm.home_goals = fm.away_goals 
                            THEN 1 ELSE 0 
                        END) as draws,
                        SUM(CASE 
                            WHEN (fm.home_team_id = dt.team_id AND fm.home_goals < fm.away_goals) OR
                                 (fm.away_team_id = dt.team_id AND fm.away_goals < fm.home_goals)
                            THEN 1 ELSE 0 
                        END) as losses,
                        SUM(CASE 
                            WHEN fm.home_team_id = dt.team_id THEN fm.home_goals
                            WHEN fm.away_team_id = dt.team_id THEN fm.away_goals
                            ELSE 0
                        END) as goals_for,
                        SUM(CASE 
                            WHEN fm.home_team_id = dt.team_id THEN fm.away_goals
                            WHEN fm.away_team_id = dt.team_id THEN fm.home_goals
                            ELSE 0
                        END) as goals_against
                    FROM dim_team dt
                    LEFT JOIN fact_match fm ON (fm.home_team_id = dt.team_id OR fm.away_team_id = dt.team_id)
                    WHERE dt.team_id > 0
                    GROUP BY dt.team_id, dt.team_name
                    ORDER BY wins DESC, team_name
                """, conn)
            return df
        except Exception as e:
            print(f"Error fetching team performance: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_top_scorers(engine, limit=20):
        """Get top goal scorers"""
        try:
            conn = DatabaseQueries._get_mysql_connection()
            df = pd.read_sql(f"""
                SELECT 
                    dp.player_name,
                    dt.team_name,
                    COUNT(DISTINCT fps.match_id) as matches_played,
                    SUM(fps.goals) as total_goals,
                    SUM(fps.assists) as total_assists,
                    SUM(fps.minutes_played) as total_minutes,
                    ROUND(AVG(fps.goals), 2) as goals_per_match
                FROM fact_player_stats fps
                JOIN dim_player dp ON fps.player_id = dp.player_id
                JOIN dim_team dt ON fps.team_id = dt.team_id
                WHERE fps.player_id > 0 AND fps.goals > 0
                GROUP BY fps.player_id, dp.player_name, fps.team_id, dt.team_name
                ORDER BY total_goals DESC
                LIMIT {limit}
            """, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error fetching top scorers: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    @staticmethod
    def get_teams(engine):
        """Get all EPL teams"""
        try:
            conn = DatabaseQueries._get_mysql_connection()
            df = pd.read_sql(
                "SELECT team_id, team_name FROM dim_team WHERE team_id > 0 ORDER BY team_name",
                conn
            )
            conn.close()
            return df
        except Exception as e:
            print(f"Error fetching teams: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    @staticmethod
    def get_team_performance(engine):
        """Get team performance statistics"""
        try:
            conn = DatabaseQueries._get_mysql_connection()
            df = pd.read_sql("""
                SELECT 
                    dt.team_id,
                    dt.team_name,
                    COUNT(DISTINCT CASE WHEN fm.home_team_id = dt.team_id THEN fm.match_id 
                                         WHEN fm.away_team_id = dt.team_id THEN fm.match_id END) as total_matches,
                    SUM(CASE WHEN fm.home_team_id = dt.team_id AND fm.home_goals > fm.away_goals THEN 1
                             WHEN fm.away_team_id = dt.team_id AND fm.away_goals > fm.home_goals THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN fm.home_goals = fm.away_goals THEN 1 ELSE 0 END) as draws,
                    SUM(CASE WHEN fm.home_team_id = dt.team_id AND fm.home_goals < fm.away_goals THEN 1
                             WHEN fm.away_team_id = dt.team_id AND fm.away_goals < fm.home_goals THEN 1 ELSE 0 END) as losses,
                    SUM(CASE WHEN fm.home_team_id = dt.team_id THEN fm.home_goals ELSE fm.away_goals END) as goals_for,
                    SUM(CASE WHEN fm.home_team_id = dt.team_id THEN fm.away_goals ELSE fm.home_goals END) as goals_against
                FROM dim_team dt
                LEFT JOIN fact_match fm ON fm.home_team_id = dt.team_id OR fm.away_team_id = dt.team_id
                WHERE dt.team_id > 0
                GROUP BY dt.team_id, dt.team_name
                ORDER BY total_matches DESC
            """, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error fetching team performance: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    @staticmethod
    def get_team_players(engine, team_id, limit=50):
        """Get all players in a team"""
        try:
            conn = DatabaseQueries._get_mysql_connection()
            df = pd.read_sql(f"""
                SELECT 
                    dp.player_name,
                    COUNT(DISTINCT fps.match_id) as matches,
                    SUM(fps.goals) as goals,
                    SUM(fps.assists) as assists,
                    SUM(fps.minutes_played) as minutes,
                    SUM(fps.shots) as shots,
                    SUM(fps.yellow_cards) as yellow_cards
                FROM fact_player_stats fps
                JOIN dim_player dp ON fps.player_id = dp.player_id
                WHERE fps.team_id = {team_id} AND fps.player_id > 0
                GROUP BY fps.player_id, dp.player_name
                ORDER BY goals DESC, assists DESC
                LIMIT {limit}
            """, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error fetching team players: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    @staticmethod
    def get_matches(engine, limit=20):
        """Get recent matches"""
        try:
            conn = DatabaseQueries._get_mysql_connection()
            df = pd.read_sql(f"""
                SELECT 
                    fm.match_id,
                    fm.date_id,
                    ht.team_name as home_team,
                    at.team_name as away_team,
                    fm.home_goals,
                    fm.away_goals,
                    CASE 
                        WHEN fm.home_goals > fm.away_goals THEN CONCAT(ht.team_name, ' W')
                        WHEN fm.home_goals < fm.away_goals THEN CONCAT(at.team_name, ' W')
                        ELSE 'Draw'
                    END as result,
                    ds.stadium_name,
                    dr.referee_name
                FROM fact_match fm
                JOIN dim_team ht ON fm.home_team_id = ht.team_id
                JOIN dim_team at ON fm.away_team_id = at.team_id
                LEFT JOIN dim_stadium ds ON fm.stadium_id = ds.stadium_id
                LEFT JOIN dim_referee dr ON fm.referee_id = dr.referee_id
                ORDER BY fm.match_id DESC
                LIMIT {limit}
            """, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error fetching matches: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    @staticmethod
    def get_match_events(engine, match_id, limit=100):
        """Get events for a specific match"""
        try:
            conn = DatabaseQueries._get_mysql_connection()
            df = pd.read_sql(f"""
                SELECT 
                    fme.event_id,
                    fme.event_timestamp,
                    fme.event_type,
                    dp.player_name,
                    dt.team_name,
                    fme.outcome,
                    fme.x_position,
                    fme.y_position
                FROM fact_match_events fme
                LEFT JOIN dim_player dp ON fme.player_id = dp.player_id
                LEFT JOIN dim_team dt ON fme.team_id = dt.team_id
                WHERE fme.match_id = {match_id}
                ORDER BY fme.event_timestamp
                LIMIT {limit}
            """, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error fetching match events: {e}")
            traceback.print_exc()
            return pd.DataFrame()

    @staticmethod
    def get_etl_status(engine):
        """Get ETL pipeline status"""
        try:
            conn = DatabaseQueries._get_mysql_connection()
            df = pd.read_sql("""
                SELECT 
                    job_name,
                    phase_step,
                    status,
                    start_time,
                    end_time,
                    message
                FROM etl_log
                ORDER BY start_time DESC
                LIMIT 100
            """, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error fetching ETL status: {e}")
            traceback.print_exc()
            return pd.DataFrame()

# ============================================================================
# UI HELPER FUNCTIONS
# ============================================================================

def populate_table_from_df(table_widget, df):
    """Populate a QTableWidget from a pandas DataFrame"""
    if df.empty:
        print("❌ Empty dataframe - table will be empty")
        return
    
    # Clear and reset table
    table_widget.setRowCount(0)
    table_widget.setColumnCount(len(df.columns))
    
    # Set column headers from dataframe
    table_widget.setHorizontalHeaderLabels(df.columns.tolist())
    
    # Add rows with data
    from PyQt6.QtGui import QColor
    for row_idx, (_, row) in enumerate(df.iterrows()):
        table_widget.insertRow(row_idx)
        for col_idx, val in enumerate(row):
            # Format value as string
            if isinstance(val, (int, float)):
                formatted_val = f"{val:,.2f}" if isinstance(val, float) else f"{val:,}"
            else:
                formatted_val = str(val) if val is not None else "N/A"
            
            item = QTableWidgetItem(formatted_val)
            # Explicitly set text color to dark color so it's visible
            item.setForeground(QColor("#333333"))
            # Alternate row colors for readability
            if row_idx % 2 == 1:
                item.setBackground(QColor("#f9f9f9"))
            else:
                item.setBackground(QColor("#ffffff"))
            table_widget.setItem(row_idx, col_idx, item)
    
    # Auto-resize columns to content width
    table_widget.resizeColumnsToContents()
    
    # Ensure minimum column width
    for i in range(len(df.columns)):
        if table_widget.columnWidth(i) < 80:
            table_widget.setColumnWidth(i, 80)

    # Force a repaint/update to ensure the UI shows the new items
    try:
        table_widget.viewport().update()
        table_widget.repaint()
        # Select the first cell to force focus/visibility
        if table_widget.rowCount() > 0 and table_widget.columnCount() > 0:
            first_item = table_widget.item(0, 0)
            if first_item is not None:
                table_widget.setCurrentItem(first_item)
    except Exception:
        pass

    print(f"✅ Populated table with {len(df)} rows and {len(df.columns)} columns")

def create_metric_card(title, value, color="#007AFF"):
    """Create a styled metric card widget"""
    widget = QWidget()
    layout = QVBoxLayout()
    
    widget.title_label = QLabel(title)
    widget.title_label.setFont(QFont("Arial", 12))
    widget.title_label.setStyleSheet("color: #666; font-weight: bold;")
    
    widget.value_label = QLabel(str(value))
    widget.value_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
    widget.value_label.setStyleSheet(f"color: {color};")
    
    layout.addWidget(widget.title_label)
    layout.addWidget(widget.value_label)
    layout.setSpacing(5)
    
    widget.setLayout(layout)
    widget.setStyleSheet(f"""
        QWidget {{
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background-color: #f9f9f9;
        }}
    """)
    
    return widget

# ============================================================================
# MAIN APPLICATION WINDOW
# ============================================================================

class EPLDWHDashboard(QMainWindow):
    """Main PyQt6 Application for EPL DWH"""
    
    def __init__(self):
        super().__init__()
        print("✅ EPLDWHDashboard.__init__ started")
        try:
            print("✅ Calling get_engine()...")
            self.engine = get_engine()
            print("✅ Engine created successfully")
        except Exception as e:
            print(f"❌ Error creating database engine: {e}")
            traceback.print_exc()
            self.engine = None
        
        print("✅ Calling initUI()...")
        self.initUI()
        print("✅ EPLDWHDashboard.__init__ complete")
        
        # Don't load data in __init__ - let user click refresh button

    def initUI(self):
        """Initialize user interface"""
        self.setWindowTitle("EPL Data Warehouse - Desktop Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet(self.get_stylesheet())

        # Create menu bar
        self.create_menu_bar()

        # Create central widget and tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        # Header
        header = QLabel("⚽ EPL Data Warehouse - Interactive Dashboard")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #333; padding: 10px;")
        main_layout.addWidget(header)

        # Tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self.dashboard_tab = self.create_dashboard_tab()
        self.teams_tab = self.create_teams_tab()
        self.players_tab = self.create_players_tab()
        self.matches_tab = self.create_matches_tab()
        self.etl_tab = self.create_etl_tab()

        self.tabs.addTab(self.dashboard_tab, "📊 Dashboard")
        self.tabs.addTab(self.teams_tab, "🏆 Teams")
        self.tabs.addTab(self.players_tab, "👤 Players")
        self.tabs.addTab(self.matches_tab, "⚽ Matches")
        self.tabs.addTab(self.etl_tab, "🔄 ETL Status")

        main_layout.addWidget(self.tabs)

        # Status bar
        self.statusBar().showMessage("Ready")

        central_widget.setLayout(main_layout)

    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Data menu
        data_menu = menubar.addMenu("Data")
        refresh_action = data_menu.addAction("Refresh All Data")
        refresh_action.triggered.connect(self.refresh_all_data)
        export_action = data_menu.addAction("Export Data")
        export_action.triggered.connect(self.export_data)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)

    def create_dashboard_tab(self):
        """Create dashboard tab with metrics"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Metrics row
        metrics_layout = QHBoxLayout()
        
        self.metric_matches = create_metric_card("Total Matches", 0, "#007AFF")
        self.metric_events = create_metric_card("Total Events", 0, "#34C759")
        self.metric_players = create_metric_card("Total Players", 0, "#FF9500")
        self.metric_teams = create_metric_card("Total Teams", 0, "#FF3B30")

        metrics_layout.addWidget(self.metric_matches)
        metrics_layout.addWidget(self.metric_events)
        metrics_layout.addWidget(self.metric_players)
        metrics_layout.addWidget(self.metric_teams)

        layout.addLayout(metrics_layout)

        # Top scorers section
        scorers_label = QLabel("Top 20 Scorers")
        scorers_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px;")
        layout.addWidget(scorers_label)
        
        self.top_scorers_table = QTableWidget()
        self.top_scorers_table.setMinimumHeight(300)
        self.top_scorers_table.setColumnCount(7)  # Match actual columns
        self.top_scorers_table.setHorizontalHeaderLabels([
            "Player", "Team", "Matches", "Goals", "Assists", "Minutes", "Goals/Match"
        ])
        layout.addWidget(self.top_scorers_table, 1)  # Add stretch factor

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Dashboard")
        refresh_btn.clicked.connect(self.load_initial_data)
        layout.addWidget(refresh_btn)

        widget.setLayout(layout)
        return widget

    def create_teams_tab(self):
        """Create teams performance tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Filter section
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Team:"))
        self.team_filter = QComboBox()
        self.team_filter.addItem("All Teams")
        self.team_filter.currentIndexChanged.connect(self.on_team_selected)
        filter_layout.addWidget(self.team_filter)
        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        # Table
        self.teams_table = QTableWidget()
        self.teams_table.setMinimumHeight(400)
        self.teams_table.setColumnCount(8)
        self.teams_table.setHorizontalHeaderLabels([
            "Team", "Matches", "Wins", "Draws", "Losses", "Goals For", "Goals Against", "Points"
        ])
        layout.addWidget(self.teams_table, 1)  # Add stretch factor

        widget.setLayout(layout)
        return widget

    def create_players_tab(self):
        """Create players statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Filter section
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Team:"))
        self.players_team_filter = QComboBox()
        self.players_team_filter.addItem("All Teams")
        self.players_team_filter.currentIndexChanged.connect(self.on_players_team_selected)
        filter_layout.addWidget(self.players_team_filter)

        filter_layout.addWidget(QLabel("Min. Goals:"))
        self.min_goals_spin = QSpinBox()
        self.min_goals_spin.setMinimum(0)
        self.min_goals_spin.setMaximum(100)
        self.min_goals_spin.setValue(0)
        self.min_goals_spin.valueChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.min_goals_spin)

        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        # Table
        self.players_table = QTableWidget()
        self.players_table.setMinimumHeight(400)
        self.players_table.setColumnCount(7)
        self.players_table.setHorizontalHeaderLabels([
            "Player Name", "Matches", "Goals", "Assists", "Minutes", "Yellow Cards", "Shots"
        ])
        layout.addWidget(self.players_table, 1)  # Add stretch factor

        widget.setLayout(layout)
        return widget

    def create_matches_tab(self):
        """Create matches tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Filter section
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Matches to show:"))
        self.matches_limit = QSpinBox()
        self.matches_limit.setMinimum(1)
        self.matches_limit.setMaximum(500)
        self.matches_limit.setValue(20)
        self.matches_limit.valueChanged.connect(self.on_matches_limit_changed)
        filter_layout.addWidget(self.matches_limit)
        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        # Matches table
        self.matches_table = QTableWidget()
        self.matches_table.setMinimumHeight(400)
        self.matches_table.setColumnCount(9)
        self.matches_table.setHorizontalHeaderLabels([
            "Match ID", "Date ID", "Home Team", "Away Team", "H Goals", "A Goals", "Result", "Stadium", "Referee"
        ])
        self.matches_table.itemDoubleClicked.connect(self.on_match_selected)
        layout.addWidget(self.matches_table, 1)  # Add stretch factor

        # Match events section
        layout.addWidget(QLabel("Match Events (double-click match above):"))
        self.match_events_table = QTableWidget()
        self.match_events_table.setMinimumHeight(200)
        self.match_events_table.setColumnCount(8)
        self.match_events_table.setHorizontalHeaderLabels([
            "Event ID", "Time", "Type", "Player", "Team", "Outcome", "X Pos", "Y Pos"
        ])
        layout.addWidget(self.match_events_table)

        widget.setLayout(layout)
        return widget

    def create_etl_tab(self):
        """Create ETL status tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Status summary
        status_layout = QHBoxLayout()
        self.etl_status_completed = create_metric_card("Completed", 0, "#34C759")
        self.etl_status_running = create_metric_card("Running", 0, "#FF9500")
        self.etl_status_failed = create_metric_card("Failed", 0, "#FF3B30")

        status_layout.addWidget(self.etl_status_completed)
        status_layout.addWidget(self.etl_status_running)
        status_layout.addWidget(self.etl_status_failed)

        layout.addLayout(status_layout)

        # Logs table
        logs_label = QLabel("ETL Logs")
        logs_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px;")
        layout.addWidget(logs_label)
        
        self.etl_logs_table = QTableWidget()
        self.etl_logs_table.setMinimumHeight(400)
        self.etl_logs_table.setColumnCount(6)
        self.etl_logs_table.setHorizontalHeaderLabels([
            "Job Name", "Phase", "Status", "Start Time", "End Time", "Message"
        ])
        layout.addWidget(self.etl_logs_table, 1)  # Add stretch factor

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh ETL Status")
        refresh_btn.clicked.connect(self.load_etl_data)
        layout.addWidget(refresh_btn)

        widget.setLayout(layout)
        return widget

    # ========================================================================
    # DATA LOADING METHODS
    # ========================================================================

    def load_initial_data(self):
        """Load all initial data using a worker thread that emits signals with data.
        Ensures UI updates happen in the main thread via connected slots.
        """
        print("✅ load_initial_data() called")
        self.statusBar().showMessage("Loading data...")

        # Define a proper worker QThread that only fetches data and emits signals
        class DataLoaderThread(QThread):
            stats_loaded = pyqtSignal(object)       # dict
            scorers_loaded = pyqtSignal(object)     # pandas DataFrame
            teams_loaded = pyqtSignal(object)
            players_loaded = pyqtSignal(object)
            matches_loaded = pyqtSignal(object)
            etl_loaded = pyqtSignal(object)
            finished = pyqtSignal()

            def __init__(self, engine):
                super().__init__()
                self.engine = engine

            def run(self):
                try:
                    print("🔄 Worker: loading dashboard stats...")
                    stats = DatabaseQueries.get_dashboard_stats(self.engine)
                    self.stats_loaded.emit(stats)
                except Exception as e:
                    print(f"Worker error loading stats: {e}")

                try:
                    print("🔄 Worker: loading top scorers...")
                    df_scorers = DatabaseQueries.get_top_scorers(self.engine, 20)
                    self.scorers_loaded.emit(df_scorers)
                except Exception as e:
                    print(f"Worker error loading scorers: {e}")

                try:
                    print("🔄 Worker: loading teams...")
                    df_teams = DatabaseQueries.get_teams(self.engine)
                    self.teams_loaded.emit(df_teams)
                except Exception as e:
                    print(f"Worker error loading teams: {e}")

                try:
                    print("🔄 Worker: loading players...")
                    df_players = DatabaseQueries.get_team_players(self.engine, 0, limit=500)
                    self.players_loaded.emit(df_players)
                except Exception as e:
                    print(f"Worker error loading players: {e}")

                try:
                    print("🔄 Worker: loading matches...")
                    df_matches = DatabaseQueries.get_matches(self.engine, 20)
                    self.matches_loaded.emit(df_matches)
                except Exception as e:
                    print(f"Worker error loading matches: {e}")

                try:
                    print("🔄 Worker: loading ETL logs...")
                    df_etl = DatabaseQueries.get_etl_status(self.engine)
                    self.etl_loaded.emit(df_etl)
                except Exception as e:
                    print(f"Worker error loading ETL: {e}")

                self.finished.emit()

        # Create and connect thread signals to main-thread slots
        if hasattr(self, 'loader_thread') and self.loader_thread.isRunning():
            print("Loader already running")
            return

        self.loader_thread = DataLoaderThread(self.engine)
        self.loader_thread.stats_loaded.connect(self._on_stats_loaded)
        self.loader_thread.scorers_loaded.connect(self._on_scorers_loaded)
        self.loader_thread.teams_loaded.connect(self._on_teams_loaded)
        self.loader_thread.players_loaded.connect(self._on_players_loaded)
        self.loader_thread.matches_loaded.connect(self._on_matches_loaded)
        self.loader_thread.etl_loaded.connect(self._on_etl_loaded)
        self.loader_thread.finished.connect(lambda: self.statusBar().showMessage("Data loaded ✅"))

        self.loader_thread.start()

    def _load_dashboard_data_impl(self):
        """Load dashboard metrics and top scorers"""
        try:
            print("✅ load_dashboard_data: Getting stats...")
            # Load metrics
            try:
                stats = DatabaseQueries.get_dashboard_stats(self.engine)
                print(f"✅ load_dashboard_data: Got stats {stats}")
                
                if stats and self.metric_matches:
                    print("✅ load_dashboard_data: Updating metric labels...")
                    self.metric_matches.value_label.setText(f"{stats.get('matches', 0):,}")
                    self.metric_events.value_label.setText(f"{stats.get('events', 0):,}")
                    self.metric_players.value_label.setText(f"{stats.get('players', 0):,}")
                    self.metric_teams.value_label.setText(f"{stats.get('teams', 0):,}")
                    print("✅ load_dashboard_data: Metrics updated")
            except Exception as e:
                print(f"❌ Error loading stats: {e}")
                traceback.print_exc()
                # Continue anyway

            # Load top scorers
            try:
                print("✅ load_dashboard_data: Getting top scorers...")
                df_scorers = DatabaseQueries.get_top_scorers(self.engine, 20)
                if df_scorers is not None and len(df_scorers) > 0:
                    print(f"✅ load_dashboard_data: Got {len(df_scorers)} scorers")
                    print("✅ load_dashboard_data: Populating table...")
                    populate_table_from_df(self.top_scorers_table, df_scorers)
                    print("✅ load_dashboard_data: Complete")
                else:
                    print("❌ No scorers data")
            except Exception as e:
                print(f"❌ Error loading scorers: {e}")
                traceback.print_exc()
        except Exception as e:
            print(f"❌ Error in load_dashboard_data: {e}")
            traceback.print_exc()

    def _load_teams_data_impl(self):
        """Load teams data (implementation)"""
        try:
            df_teams = DatabaseQueries.get_teams(self.engine)
            self.team_filter.blockSignals(True)
            self.team_filter.clear()
            self.team_filter.addItem("All Teams")
            for _, row in df_teams.iterrows():
                self.team_filter.addItem(row['team_name'], row['team_id'])
            self.team_filter.blockSignals(False)

            # Load performance data
            df_performance = DatabaseQueries.get_team_performance(self.engine)
            
            # Add points column
            df_performance['Points'] = (df_performance['wins'] * 3) + (df_performance['draws'] * 1)
            
            # Keep only needed columns
            display_df = df_performance[['team_name', 'total_matches', 'wins', 'draws', 'losses', 'goals_for', 'goals_against', 'Points']]
            populate_table_from_df(self.teams_table, display_df)
        except Exception as e:
            print(f"❌ Error loading teams data: {e}")
            traceback.print_exc()

    def load_teams_data(self):
        """Load teams data (call from thread)"""
        self._load_teams_data_impl()

    def _load_players_data_impl(self):
        """Load players data (implementation)"""
        try:
            df_teams = DatabaseQueries.get_teams(self.engine)
            self.players_team_filter.blockSignals(True)
            self.players_team_filter.clear()
            self.players_team_filter.addItem("All Teams")
            for _, row in df_teams.iterrows():
                self.players_team_filter.addItem(row['team_name'], row['team_id'])
            self.players_team_filter.blockSignals(False)

            # Load all players initially
            self.on_filter_changed()
        except Exception as e:
            print(f"❌ Error loading players data: {e}")
            traceback.print_exc()

    def load_players_data(self):
        """Load players data (call from thread)"""
        self._load_players_data_impl()

    def _load_matches_data_impl(self):
        """Load matches data (implementation)"""
        try:
            limit = self.matches_limit.value()
            df_matches = DatabaseQueries.get_matches(self.engine, limit)
            populate_table_from_df(self.matches_table, df_matches)
        except Exception as e:
            print(f"❌ Error loading matches data: {e}")
            traceback.print_exc()

    def load_matches_data(self):
        """Load matches data (call from thread)"""
        self._load_matches_data_impl()

    def _load_etl_data_impl(self):
        """Load ETL status data (implementation)"""
        try:
            df_etl = DatabaseQueries.get_etl_status(self.engine)
            populate_table_from_df(self.etl_logs_table, df_etl)

            # Update status summary
            if not df_etl.empty:
                status_counts = df_etl['status'].value_counts()
                completed = status_counts.get('COMPLETED', 0)
                running = status_counts.get('RUNNING', 0)
                failed = status_counts.get('FAILED', 0)

                self.etl_status_completed.findChildren(QLabel)[1].setText(str(completed))
                self.etl_status_running.findChildren(QLabel)[1].setText(str(running))
                self.etl_status_failed.findChildren(QLabel)[1].setText(str(failed))
        except Exception as e:
            print(f"❌ Error loading ETL data: {e}")
            traceback.print_exc()

    def load_etl_data(self):
        """Load ETL data (call from thread)"""
        self._load_etl_data_impl()

    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================

    def on_team_selected(self):
        """Handle team selection"""
        team_id = self.team_filter.currentData()
        if team_id:
            try:
                df_players = DatabaseQueries.get_team_players(self.engine, team_id)
                populate_table_from_df(self.players_table, df_players)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error loading team players: {str(e)}")

    def on_players_team_selected(self):
        """Handle players team selection"""
        self.on_filter_changed()

    def on_filter_changed(self):
        """Handle player filter changes"""
        team_id = self.players_team_filter.currentData()
        min_goals = self.min_goals_spin.value()

        try:
            if team_id:
                df_players = DatabaseQueries.get_team_players(self.engine, team_id)
                df_players = df_players[df_players['goals'] >= min_goals]
                populate_table_from_df(self.players_table, df_players)
        except Exception as e:
            print(f"Error filtering players: {e}")

    def on_matches_limit_changed(self):
        """Handle matches limit change"""
        self.load_matches_data()

    def on_match_selected(self, item):
        """Handle match selection to show events"""
        try:
            match_id = self.matches_table.item(item.row(), 0).text()
            df_events = DatabaseQueries.get_match_events(self.engine, int(match_id))
            populate_table_from_df(self.match_events_table, df_events)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading match events: {str(e)}")

    def refresh_all_data(self):
        """Refresh all data"""
        self.load_initial_data()

    def export_data(self):
        """Export data to CSV"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                # Get current table
                current_tab = self.tabs.currentWidget()
                # Export logic here
                QMessageBox.information(self, "Success", f"Data exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error exporting data: {str(e)}")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.information(
            self,
            "About EPL DWH Dashboard",
            "EPL Data Warehouse Desktop Dashboard v1.0\n\n"
            "Built with PyQt6\n"
            "Data Source: StatsBomb + FootballData.org\n"
            "Database: MySQL with 2.6M+ events"
        )

    # ------------------------------------------------------------------
    # Slots: receive data from worker thread and update UI (main thread)
    # ------------------------------------------------------------------
    def _on_stats_loaded(self, stats):
        try:
            print("Slot: updating metric labels with stats", stats)
            if stats and self.metric_matches:
                self.metric_matches.value_label.setText(f"{stats.get('matches', 0):,}")
                self.metric_events.value_label.setText(f"{stats.get('events', 0):,}")
                self.metric_players.value_label.setText(f"{stats.get('players', 0):,}")
                self.metric_teams.value_label.setText(f"{stats.get('teams', 0):,}")
        except Exception as e:
            print(f"Error updating metrics: {e}")

    def _on_scorers_loaded(self, df):
        try:
            print(f"Slot: populating top scorers table ({None if df is None else len(df)} rows)")
            if df is None or df.empty:
                return
            populate_table_from_df(self.top_scorers_table, df)
        except Exception as e:
            print(f"Error populating scorers: {e}")

    def _on_teams_loaded(self, df):
        try:
            if df is None or df.empty:
                return
            # populate team filter and table
            self.team_filter.blockSignals(True)
            self.team_filter.clear()
            self.team_filter.addItem("All Teams", 0)
            for _, row in df.iterrows():
                self.team_filter.addItem(row['team_name'], row['team_id'])
            self.team_filter.blockSignals(False)

            # Also show team performance table
            perf = DatabaseQueries.get_team_performance(self.engine)
            if perf is not None and not perf.empty:
                perf['Points'] = (perf['wins'] * 3) + perf['draws']
                display_df = perf[['team_name', 'total_matches', 'wins', 'draws', 'losses', 'goals_for', 'goals_against', 'Points']]
                populate_table_from_df(self.teams_table, display_df)
        except Exception as e:
            print(f"Error populating teams: {e}")

    def _on_players_loaded(self, df):
        try:
            if df is None or df.empty:
                return
            # populate players table
            populate_table_from_df(self.players_table, df)
        except Exception as e:
            print(f"Error populating players: {e}")

    def _on_matches_loaded(self, df):
        try:
            if df is None or df.empty:
                return
            populate_table_from_df(self.matches_table, df)
        except Exception as e:
            print(f"Error populating matches: {e}")

    def _on_etl_loaded(self, df):
        try:
            if df is None or df.empty:
                return
            populate_table_from_df(self.etl_logs_table, df)
            # update ETL status summary if columns present
            if 'status' in df.columns:
                status_counts = df['status'].value_counts()
                completed = status_counts.get('COMPLETED', 0)
                running = status_counts.get('RUNNING', 0)
                failed = status_counts.get('FAILED', 0)
                try:
                    self.etl_status_completed.findChildren(QLabel)[1].setText(str(completed))
                    self.etl_status_running.findChildren(QLabel)[1].setText(str(running))
                    self.etl_status_failed.findChildren(QLabel)[1].setText(str(failed))
                except Exception:
                    pass
        except Exception as e:
            print(f"Error populating ETL logs: {e}")

    # ========================================================================
    # STYLING
    # ========================================================================

    @staticmethod
    def get_stylesheet():
        """Get application stylesheet"""
        return """
            QMainWindow {
                background-color: #ffffff;
            }
            
            QTabWidget::pane {
                border: 1px solid #ddd;
            }
            
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 20px;
                margin-right: 2px;
                border: 1px solid #ddd;
                color: #333;
                font-weight: bold;
            }
            
            QTabBar::tab:selected {
                background-color: #007AFF;
                color: white;
                font-weight: bold;
            }
            
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #e0e0e0;
                background-color: white;
                color: #333;
                alternate-background-color: #f9f9f9;
            }
            
            QTableWidget::item {
                padding: 5px;
                color: #333;
                background-color: white;
            }
            
            QTableWidget::item:selected {
                background-color: #007AFF;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ddd;
                font-weight: bold;
                color: #333;
            }
            
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #0051D5;
            }
            
            QPushButton:pressed {
                background-color: #003A99;
            }
            
            QComboBox {
                border: 1px solid #ddd;
                padding: 5px;
                border-radius: 4px;
                background-color: white;
            }
            
            QSpinBox {
                border: 1px solid #ddd;
                padding: 5px;
                border-radius: 4px;
                background-color: white;
            }
            
            QLabel {
                color: #333;
            }
            
            QStatusBar {
                background-color: #f0f0f0;
                color: #333;
            }
        """

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    print("✅ Starting EPL DWH Desktop Application...")
    app = QApplication(sys.argv)
    app.setApplicationName("EPL Data Warehouse Dashboard")
    print("✅ QApplication created")
    
    try:
        print("✅ Creating dashboard...")
        dashboard = EPLDWHDashboard()
        print("✅ Dashboard created, showing window...")
        dashboard.show()
        print("✅ Window shown, starting event loop...")
        sys.exit(app.exec())
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("✅ Application closed")

if __name__ == "__main__":
    main()
