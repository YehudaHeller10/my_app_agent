import os
import re
import json
import time
from typing import Dict, List, Any, Optional, Callable
from core.llm_manager import LLMManager
from core.android_templates import AndroidTemplates


class ProjectGenerator:
    """
    Generates complete Android Studio projects from AI-generated code
    """

    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
        self.templates = AndroidTemplates()

        # Project configuration
        self.default_config = {
            'min_sdk': 24,
            'target_sdk': 34,
            'compile_sdk': 34,
            'kotlin_version': '1.9.24',
            'gradle_version': '8.5.2',
            'room_version': '2.6.1',
            'retrofit_version': '2.9.0',
            'material_version': '1.12.0'
        }

    def generate_project(self,
                         project_name: str,
                         description: str,
                         output_dir: str,
                         config: Optional[Dict] = None,
                         progress_callback: Optional[Callable[[str, str, str], None]] = None) -> Dict[str, Any]:
        """
        Generate a complete Android project

        Args:
            project_name: Name of the project
            description: Project description/requirements
            output_dir: Output directory for the project
            config: Optional project configuration

        Returns:
            Dict with success status and project information
        """
        try:
            # Validate inputs
            if not project_name or not project_name.strip():
                raise ValueError("Project name cannot be empty")

            if not description or not description.strip():
                raise ValueError("Project description cannot be empty")

            if not output_dir or not os.path.exists(output_dir):
                raise ValueError(f"Output directory does not exist: {output_dir}")

            # Sanitize project name
            project_name = self._sanitize_project_name(project_name)

            # Merge configuration
            project_config = self.default_config.copy()
            if config:
                project_config.update(config)

            # Create project directory
            project_path = os.path.join(output_dir, project_name)

            # Check if project already exists
            if os.path.exists(project_path):
                raise ValueError(f"Project directory already exists: {project_path}")

            if progress_callback:
                progress_callback("create_structure", "Creating project structure", "start")
            os.makedirs(project_path, exist_ok=True)

            # Generate project structure
            self._create_project_structure(project_path, project_name, project_config)
            if progress_callback:
                progress_callback("create_structure", "Creating project structure", "done")

            # Generate project files
            if progress_callback:
                progress_callback("gradle_files", "Generating Gradle and settings files", "start")
            self._generate_project_files(project_path, project_name, description, project_config)
            if progress_callback:
                progress_callback("gradle_files", "Generating Gradle and settings files", "done")

            # Generate app-specific code
            if progress_callback:
                progress_callback("app_code", "Generating app source and resources", "start")
            self._generate_app_code(project_path, project_name, description, project_config)
            if progress_callback:
                progress_callback("app_code", "Generating app source and resources", "done")

            # Create README
            if progress_callback:
                progress_callback("readme", "Creating README", "start")
            self._create_readme(project_path, project_name, description)
            if progress_callback:
                progress_callback("readme", "Creating README", "done")

            return {
                'success': True,
                'project_path': project_path,
                'project_name': project_name,
                'config': project_config,
                'timestamp': time.time()
            }

        except Exception as e:
            print(f"Project generation error: {e}")
            if progress_callback:
                progress_callback("error", str(e), "error")
            return {
                'success': False,
                'error': str(e),
                'project_path': None
            }

    def _create_project_structure(self, project_path: str, project_name: str, config: Dict):
        """Create the basic project directory structure"""
        # Main project directories
        app_dir = os.path.join(project_path, "app")
        src_main = os.path.join(app_dir, "src", "main")

        # Create directories
        directories = [
            app_dir,
            src_main,
            os.path.join(src_main, "java"),
            os.path.join(src_main, "res"),
            os.path.join(src_main, "res", "layout"),
            os.path.join(src_main, "res", "values"),
            os.path.join(src_main, "res", "drawable"),
            os.path.join(src_main, "res", "mipmap-hdpi"),
            os.path.join(src_main, "res", "mipmap-mdpi"),
            os.path.join(src_main, "res", "mipmap-xhdpi"),
            os.path.join(src_main, "res", "mipmap-xxhdpi"),
            os.path.join(src_main, "res", "mipmap-xxxhdpi"),
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def _generate_project_files(self, project_path: str, project_name: str, description: str, config: Dict):
        """Generate project-level files"""
        # settings.gradle
        settings_content = f"""include ':app'
rootProject.name = '{project_name}'
"""
        self._write_file(os.path.join(project_path, "settings.gradle"), settings_content, progress_callback=None)

        # Project-level build.gradle
        project_build_content = f"""// Top-level build file
buildscript {{
    repositories {{
        google()
        mavenCentral()
    }}
    dependencies {{
        classpath 'com.android.tools.build:gradle:{config['gradle_version']}'
        classpath 'org.jetbrains.kotlin:kotlin-gradle-plugin:{config['kotlin_version']}'
    }}
}}

allprojects {{
    repositories {{
        google()
        mavenCentral()
    }}
}}

tasks.register("clean", Delete) {{
    delete rootProject.buildDir
}}
"""
        self._write_file(os.path.join(project_path, "build.gradle"), project_build_content, progress_callback=None)

        # gradle.properties
        gradle_props = """# Project-wide Gradle settings
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
kotlin.code.style=official
"""
        self._write_file(os.path.join(project_path, "gradle.properties"), gradle_props, progress_callback=None)

        # gradle wrapper files
        self._create_gradle_wrapper(project_path)

    def _generate_app_code(self, project_path: str, project_name: str, description: str, config: Dict):
        """Generate app-specific code and resources"""
        app_dir = os.path.join(project_path, "app")
        src_main = os.path.join(app_dir, "src", "main")

        # Determine package name
        package_name = f"com.example.{project_name.lower().replace(' ', '')}"

        # Create package directory structure
        package_dir = os.path.join(src_main, "java")
        for package_part in package_name.split('.'):
            package_dir = os.path.join(package_dir, package_part)
        os.makedirs(package_dir, exist_ok=True)

        # Generate app-level build.gradle
        app_build_content = self._generate_app_build_gradle(package_name, config)
        self._write_file(os.path.join(app_dir, "build.gradle"), app_build_content)

        # Generate AndroidManifest.xml
        manifest_content = self._generate_android_manifest(package_name, project_name)
        self._write_file(os.path.join(src_main, "AndroidManifest.xml"), manifest_content)

        # Generate MainActivity
        main_activity_content = self._generate_main_activity(package_name, project_name)
        self._write_file(os.path.join(package_dir, "MainActivity.kt"), main_activity_content)

        # Generate layout files
        self._generate_layout_files(src_main, project_name)

        # Generate resource files
        self._generate_resource_files(src_main, project_name)

        # Generate additional components based on description
        self._generate_additional_components(package_dir, package_name, description, config)

    def _generate_app_build_gradle(self, package_name: str, config: Dict) -> str:
        """Generate app-level build.gradle file"""
        return f"""plugins {{
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
    id 'kotlin-kapt'
}}

android {{
    namespace '{package_name}'
    compileSdk {config['compile_sdk']}

    defaultConfig {{
        applicationId '{package_name}'
        minSdk {config['min_sdk']}
        targetSdk {config['target_sdk']}
        versionCode 1
        versionName "1.0"

        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
    }}

    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}

    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}

    kotlinOptions {{
        jvmTarget = '1.8'
    }}

    buildFeatures {{
        viewBinding true
    }}
}}

dependencies {{
    implementation 'androidx.core:core-ktx:1.13.1'
    implementation 'androidx.appcompat:appcompat:1.7.0'
    implementation 'com.google.android.material:material:{config['material_version']}'
    implementation 'androidx.constraintlayout:constraintlayout:2.2.0'
    implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0'
    implementation 'androidx.lifecycle:lifecycle-livedata-ktx:2.7.0'
    implementation 'androidx.recyclerview:recyclerview:1.3.2'
    implementation 'androidx.cardview:cardview:1.0.0'

    // Room Database
    implementation 'androidx.room:room-runtime:{config['room_version']}'
    implementation 'androidx.room:room-ktx:{config['room_version']}'
    kapt 'androidx.room:room-compiler:{config['room_version']}'

    // Retrofit for API calls
    implementation 'com.squareup.retrofit2:retrofit:{config['retrofit_version']}'
    implementation 'com.squareup.retrofit2:converter-gson:{config['retrofit_version']}'
    implementation 'com.squareup.okhttp3:logging-interceptor:4.12.0'

    // Coroutines
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'

    // Navigation
    implementation 'androidx.navigation:navigation-fragment-ktx:2.7.7'
    implementation 'androidx.navigation:navigation-ui-ktx:2.7.7'

    // Testing
    testImplementation 'junit:junit:4.13.2'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
}}
"""

    def _generate_android_manifest(self, package_name: str, project_name: str) -> str:
        """Generate AndroidManifest.xml"""
        return f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="{project_name}"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.{project_name.replace(' ', '')}"
        tools:targetApi="31">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.{project_name.replace(' ', '')}.Main">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
"""

    def _generate_main_activity(self, package_name: str, project_name: str) -> str:
        """Generate MainActivity.kt"""
        return f"""package {package_name}

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import {package_name}.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {{
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupUI()
    }}

    private fun setupUI() {{
        // Initialize your UI components here
        binding.titleText.text = "Welcome to {project_name}!"
    }}
}}
"""

    def _generate_layout_files(self, src_main: str, project_name: str):
        """Generate layout files"""
        layout_dir = os.path.join(src_main, "res", "layout")

        # Main activity layout
        main_layout = f"""<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <TextView
        android:id="@+id/titleText"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Welcome to {project_name}!"
        android:textSize="24sp"
        android:textStyle="bold"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
"""
        self._write_file(os.path.join(layout_dir, "activity_main.xml"), main_layout)

    def _generate_resource_files(self, src_main: str, project_name: str):
        """Generate resource files"""
        values_dir = os.path.join(src_main, "res", "values")

        # strings.xml
        strings_content = f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{project_name}</string>
    <string name="welcome_message">Welcome to {project_name}!</string>
</resources>
"""
        self._write_file(os.path.join(values_dir, "strings.xml"), strings_content)

        # colors.xml
        colors_content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="purple_200">#FFBB86FC</color>
    <color name="purple_500">#FF6200EE</color>
    <color name="purple_700">#FF3700B3</color>
    <color name="teal_200">#FF03DAC5</color>
    <color name="teal_700">#FF018786</color>
    <color name="black">#FF000000</color>
    <color name="white">#FFFFFFFF</color>
</resources>
"""
        self._write_file(os.path.join(values_dir, "colors.xml"), colors_content)

        # themes.xml
        theme_name = project_name.replace(' ', '')
        themes_content = f"""<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:tools="http://schemas.android.com/tools">
    <!-- Base application theme. -->
    <style name="Theme.{theme_name}" parent="Theme.MaterialComponents.DayNight.DarkActionBar">
        <!-- Primary brand color. -->
        <item name="colorPrimary">@color/purple_500</item>
        <item name="colorPrimaryVariant">@color/purple_700</item>
        <item name="colorOnPrimary">@color/white</item>
        <!-- Secondary brand color. -->
        <item name="colorSecondary">@color/teal_200</item>
        <item name="colorSecondaryVariant">@color/teal_700</item>
        <item name="colorOnSecondary">@color/black</item>
        <!-- Status bar color. -->
        <item name="android:statusBarColor" tools:targetApi="l">?attr/colorPrimaryVariant</item>
        <!-- Customize your theme here. -->
    </style>

    <style name="Theme.{theme_name}.Main" parent="Theme.MaterialComponents.DayNight.NoActionBar">
        <item name="colorPrimary">@color/purple_500</item>
        <item name="colorPrimaryVariant">@color/purple_700</item>
        <item name="colorOnPrimary">@color/white</item>
        <item name="colorSecondary">@color/teal_200</item>
        <item name="colorSecondaryVariant">@color/teal_700</item>
        <item name="colorOnSecondary">@color/black</item>
        <item name="android:statusBarColor" tools:targetApi="l">?attr/colorPrimaryVariant</item>
    </style>
</resources>
"""
        self._write_file(os.path.join(values_dir, "themes.xml"), themes_content)

        # Create additional resource files
        self._create_additional_resources(values_dir)

    def _create_additional_resources(self, values_dir: str):
        """Create additional resource files"""
        # backup_rules.xml
        backup_rules = """<?xml version="1.0" encoding="utf-8"?>
<full-backup-content>
    <!-- Exclude specific files or directories from backup -->
</full-backup-content>
"""
        self._write_file(os.path.join(values_dir, "backup_rules.xml"), backup_rules)

        # data_extraction_rules.xml
        data_extraction_rules = """<?xml version="1.0" encoding="utf-8"?>
<data-extraction-rules>
    <cloud-backup>
        <!-- TODO: Use <include> and <exclude> to control what is backed up.
        <include .../>
        <exclude .../>
        -->
    </cloud-backup>
    <!--
    <device-transfer>
        <include .../>
        <exclude .../>
    </device-transfer>
    -->
</data-extraction-rules>
"""
        self._write_file(os.path.join(values_dir, "data_extraction_rules.xml"), data_extraction_rules)

    def _generate_additional_components(self, package_dir: str, package_name: str, description: str, config: Dict):
        """Generate additional components based on project description"""
        # Analyze description to determine what components to generate
        description_lower = description.lower()

        # Generate data models if needed
        if any(keyword in description_lower for keyword in ['database', 'room', 'data', 'model']):
            self._generate_data_models(package_dir, package_name)

        # Generate API service if needed
        if any(keyword in description_lower for keyword in ['api', 'network', 'http', 'retrofit']):
            self._generate_api_service(package_dir, package_name)

        # Generate adapters if needed
        if any(keyword in description_lower for keyword in ['list', 'recycler', 'adapter']):
            self._generate_adapters(package_dir, package_name)

        # Generate view models if needed
        if any(keyword in description_lower for keyword in ['viewmodel', 'mvvm', 'architecture']):
            self._generate_view_models(package_dir, package_name)

    def _generate_data_models(self, package_dir: str, package_name: str):
        """Generate data models and Room database"""
        data_dir = os.path.join(package_dir, "data")
        os.makedirs(data_dir, exist_ok=True)

        # Example data model
        data_model = f"""package {package_name}.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "items")
data class Item(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val description: String,
    val isCompleted: Boolean = false
)
"""
        self._write_file(os.path.join(data_dir, "Item.kt"), data_model)

        # DAO
        dao = f"""package {package_name}.data

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Dao
interface ItemDao {{
    @Query("SELECT * FROM items")
    fun getAllItems(): Flow<List<Item>>

    @Insert
    suspend fun insertItem(item: Item)

    @Update
    suspend fun updateItem(item: Item)

    @Delete
    suspend fun deleteItem(item: Item)
}}
"""
        self._write_file(os.path.join(data_dir, "ItemDao.kt"), dao)

        # Database
        database = f"""package {package_name}.data

import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import android.content.Context

@Database(entities = [Item::class], version = 1)
abstract class AppDatabase : RoomDatabase() {{
    abstract fun itemDao(): ItemDao

    companion object {{
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {{
            return INSTANCE ?: synchronized(this) {{
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "app_database"
                ).build()
                INSTANCE = instance
                instance
            }}
        }}
    }}
}}
"""
        self._write_file(os.path.join(data_dir, "AppDatabase.kt"), database)

    def _generate_api_service(self, package_dir: str, package_name: str):
        """Generate API service and network components"""
        network_dir = os.path.join(package_dir, "network")
        os.makedirs(network_dir, exist_ok=True)

        # API service interface
        api_service = f"""package {package_name}.network

import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Body

interface ApiService {{
    @GET("items")
    suspend fun getItems(): List<Item>

    @POST("items")
    suspend fun createItem(@Body item: Item): Item
}}
"""
        self._write_file(os.path.join(network_dir, "ApiService.kt"), api_service)

        # Network module
        network_module = f"""package {package_name}.network

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object NetworkModule {{
    private const val BASE_URL = "https://api.example.com/"

    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    val apiService: ApiService = retrofit.create(ApiService::class.java)
}}
"""
        self._write_file(os.path.join(network_dir, "NetworkModule.kt"), network_module)

    def _generate_adapters(self, package_dir: str, package_name: str):
        """Generate RecyclerView adapters"""
        adapter_dir = os.path.join(package_dir, "ui", "adapter")
        os.makedirs(adapter_dir, exist_ok=True)

        # Example adapter
        adapter = f"""package {package_name}.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import {package_name}.data.Item
import {package_name}.databinding.ItemLayoutBinding

class ItemAdapter(
    private val onItemClick: (Item) -> Unit,
    private val onItemLongClick: (Item) -> Boolean
) : ListAdapter<Item, ItemAdapter.ItemViewHolder>(ItemDiffCallback()) {{

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ItemViewHolder {{
        val binding = ItemLayoutBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ItemViewHolder(binding)
    }}

    override fun onBindViewHolder(holder: ItemViewHolder, position: Int) {{
        holder.bind(getItem(position))
    }}

    inner class ItemViewHolder(
        private val binding: ItemLayoutBinding
    ) : RecyclerView.ViewHolder(binding.root) {{

        fun bind(item: Item) {{
            binding.itemTitle.text = item.title
            binding.itemDescription.text = item.description
            binding.itemCheckbox.isChecked = item.isCompleted

            binding.root.setOnClickListener {{ onItemClick(item) }}
            binding.root.setOnLongClickListener {{ onItemLongClick(item) }}
        }}
    }}

    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {{
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {{
            return oldItem.id == newItem.id
        }}

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {{
            return oldItem == newItem
        }}
    }}
}}
"""
        self._write_file(os.path.join(adapter_dir, "ItemAdapter.kt"), adapter)

    def _generate_view_models(self, package_dir: str, package_name: str):
        """Generate ViewModels"""
        viewmodel_dir = os.path.join(package_dir, "ui", "viewmodel")
        os.makedirs(viewmodel_dir, exist_ok=True)

        # Main ViewModel
        viewmodel = f"""package {package_name}.ui.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.launch
import {package_name}.data.Item
import {package_name}.data.ItemDao

class MainViewModel(private val itemDao: ItemDao) : ViewModel() {{

    private val _items = MutableLiveData<List<Item>>()
    val items: LiveData<List<Item>> = _items

    init {{
        loadItems()
    }}

    private fun loadItems() {{
        viewModelScope.launch {{
            itemDao.getAllItems().collect {{ items ->
                _items.value = items
            }}
        }}
    }}

    fun addItem(title: String, description: String) {{
        viewModelScope.launch {{
            val item = Item(title = title, description = description)
            itemDao.insertItem(item)
        }}
    }}

    fun updateItem(item: Item) {{
        viewModelScope.launch {{
            itemDao.updateItem(item)
        }}
    }}

    fun deleteItem(item: Item) {{
        viewModelScope.launch {{
            itemDao.deleteItem(item)
        }}
    }}
}}
"""
        self._write_file(os.path.join(viewmodel_dir, "MainViewModel.kt"), viewmodel)

    def _create_gradle_wrapper(self, project_path: str):
        """Create Gradle wrapper files"""
        gradle_wrapper_dir = os.path.join(project_path, "gradle", "wrapper")
        os.makedirs(gradle_wrapper_dir, exist_ok=True)

        # gradle-wrapper.properties
        wrapper_props = """distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
        distributionUrl=https://services.gradle.org/distributions/gradle-8.5-bin.zip
networkTimeout=10000
validateDistributionUrl=true
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
"""
        self._write_file(os.path.join(gradle_wrapper_dir, "gradle-wrapper.properties"), wrapper_props)

        # Create gradlew scripts (simplified)
        gradlew_content = """#!/bin/sh
# Gradle startup script for Unix
exec "$JAVACMD" "$@"
"""
        self._write_file(os.path.join(project_path, "gradlew"), gradlew_content)

        # Make gradlew executable
        try:
            os.chmod(os.path.join(project_path, "gradlew"), 0o755)
        except:
            pass

    def _create_readme(self, project_path: str, project_name: str, description: str):
        """Create README file for the project"""
        readme_content = f"""# {project_name}

{description}

## Getting Started

1. Open the project in Android Studio
2. Sync Gradle dependencies
3. Build and run the project

## Project Structure

- `app/src/main/java/` - Kotlin source code
- `app/src/main/res/` - Resources (layouts, strings, etc.)
- `app/src/main/AndroidManifest.xml` - App manifest

## Features

- Modern Android development with Kotlin
- Material Design UI components
- MVVM architecture
- Room database for data persistence
- Retrofit for API calls

## Requirements

- Android Studio Arctic Fox or later
- Android SDK 24+
- Kotlin 1.9.24+

## Build Instructions

```bash
# Clone the project
git clone <repository-url>
cd {project_name}

# Open in Android Studio
# Or build from command line
./gradlew assembleDebug
```

Generated by Android App Generator
"""
        self._write_file(os.path.join(project_path, "README.md"), readme_content)

    def _write_file(self, file_path: str, content: str, progress_callback: Optional[Callable[[str, str, str], None]] = None):
        """Write content to file with proper encoding and emit progress events"""
        try:
            if progress_callback:
                display = os.path.basename(file_path)
                progress_callback(f"file_{display}", f"Creating {display}", "start")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            if progress_callback:
                display = os.path.basename(file_path)
                progress_callback(f"file_{display}", f"Creating {display}", "done")
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")
            if progress_callback:
                progress_callback(f"file_{os.path.basename(file_path)}", f"Creating {os.path.basename(file_path)} failed", "error")
            raise

    def _sanitize_project_name(self, project_name: str) -> str:
        """Sanitize project name for valid directory name"""
        # Remove invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', project_name)
        # Replace spaces with underscores
        sanitized = re.sub(r'\s+', '_', sanitized)
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('._ ')
        # Ensure it's not empty
        if not sanitized:
            sanitized = "AndroidProject"
        # Limit length
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        return sanitized