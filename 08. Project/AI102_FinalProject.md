# Project Outline: AI-Driven Auto Shop Inspection & Decision System

## Project Overview:

This project aims to build an intelligent, automated inspection and decision-making system for a fictional auto repair shop, leveraging Azure AI Foundry and Azure AI services. The system will automate image quality validation, streamline inspection workflows via multilingual voice-to-text capabilities, and determine repair feasibility based on insurance policies.

---

## 1. Image Quality Validation System

### 1.1 Image Quality Assessment

**Objective:**
Automatically validate images for quality assurance before insurance submission. If an image does not meet the quality criteria, it will be flagged for retake.

**AI Capabilities:**

* **Blur Detection:**
  Detect blurred images using image clarity analysis.

* **Exposure Analysis:**
  Detect and flag overexposed or underexposed images.

* **Lighting Condition Check:**
  Evaluate lighting conditions; identify images with excessive glare or insufficient illumination.

* **Content-Specific Validation:**

  * Validate odometer reading clarity from dashboard images (Azure OCR/Vision).
  * Ensure license plate readability.

**Action:**
Automatically mark images requiring a retake if they fail quality criteria.

**Input:**

* Digital images (JPEG/PNG)

**Output:**

* Quality Score (numeric value)
* Detailed feedback for each flagged image (e.g., "Image blurred," "License plate unreadable," etc.)

---

### 1.2 Damage Detection and Documentation

**Objective:**
Automatically identify, catalog, and estimate the costs of visible vehicle damage from submitted images.

**AI Capabilities:**

* **Cosmetic Damage Detection:**
  Train Custom Vision to identify and categorize cosmetic issues like scratches, dents, and paint damage.

* **Mechanical Damage Indicators:**
  Identify visual indicators of mechanical damage (e.g., misaligned wheels, broken parts).

* **Damage Mapping:**
  Generate spatial mapping of identified damage locations on a standardized vehicle model schematic.

* **Measurement and Cost Estimation:**
  Extract visible measurements (e.g., length of crack) using OCR and map extracted damages to repair costs from internal knowledge base.

**Input:**

* Digital images from inspection

**Output:**

* Categorized damage report (type, location, severity)
* Visual damage map
* Preliminary repair cost estimation (linked to internal data)


## 2. Voice-to-Text Inspection System

### 2.1 Multilingual Voice Recognition

**Objective:**
Enable real-time transcription of inspection notes from inspectors using natural speech in English and Spanish.

**AI Capabilities:**

* **Speech-to-Text Conversion:**
  Real-time transcription from English or Spanish speech into English text.

* **Domain-Specific Model Tuning:**
  Customize speech recognition models specifically to automotive terminology.

**Accuracy Goal:**

* Minimum 95% transcription accuracy for specialized automotive terms and conditions.

**Input:**

* Real-time audio stream from inspector (via mobile/tablet app or web interface)

**Output:**

* Real-time transcription text (English)


### 2.2 Contextual Form Filling

**Objective:**
Automatically populate standardized vehicle inspection forms based on voice input.

**AI Capabilities:**

* **Automotive Terminology Recognition:**
  Train CLU/GPT-4o models to understand automotive-specific language and terminology.

* **Contextual Understanding:**
  Convert natural speech into structured form entries. Examples:

  * `"windshield cracked two inches"` → Form Entry:

    * Part: Windshield
    * Condition: Cracked
    * Notes: "Crack length: 2 inches"
  * `"front tire thread depth four"` → Form Entry:

    * Part: Front Tire
    * Condition: Needs Replacement
    * Notes: "Thread depth: 4mm"

* **Measurement Extraction:**
  Identify and document precise measurements from verbal descriptions.

**Input:**

* Real-time or recorded voice transcription

**Output:**

* Completed digital inspection forms
* Highlighted inspection points requiring manual review or action


## 3. Repair/Total Loss Decision Engine (Stretch Goal)

### 3.1 Policy-Based Assessment

**Objective:**
Automate the determination of repair feasibility or total loss status based on specific insurance policies and internal criteria.

**Data Sources (Internal Azure Database and/or AI Search Service):**
All of these sources would need to be spoofed or simulated beforehand, as the nature of the data would change the nuances of the solution.

* Shady Company policy database 
* Trust Co policy database
* Internal repair cost database
* Parts availability database

**Constraints:**

* System restricted exclusively to internal data sources; external lookups prohibited.

**Capabilities:**

* Policy rule matching
* Cost-to-repair vs. total loss threshold analysis
* Availability check for required parts in internal databases


### 3.2 Decision Logic

**Objective:**
Clearly justify and communicate the decision-making process regarding repair feasibility.

**Decision Workflow:**

* **Step 1:** Aggregate all inspection inputs (damage report, inspection form data, photos).
* **Step 2:** Cross-reference damages and cost estimations with insurance policy rules.
* **Step 3:** Perform repair cost vs. total loss threshold analysis.
* **Step 4:** Validate parts availability internally.
* **Step 5:** Generate final decision (Repairable or Total Loss) with structured justification.


**Input:**

* Completed inspection forms
* Damage reports
* Vehicle specifications (year, model, mileage)
* Insurance policy details

**Output:**

* Final repair recommendation ("Repairable"/"Total Loss")
* Justification report (with breakdown of decision factors and policy rules triggered)


# Solution Guidance -- Functional Requirements 1 and 2
*feel free to deviate from this*

## Service Selection
### Using "Traditional" Azure AI Services

#### Image Quality Assessment

* Image Quality Assessment: The Azure AI Vision service (Computer Vision API) can perform general image analysis (object detection, tags, etc.), but specific quality checks like blur or exposure require custom handling. One approach is to train a Custom Vision classification model to recognize unacceptable blur or lighting – e.g. tagging images as “blurry” vs “clear,” “well-lit” vs “underexposed.”

* Content-Specific Validation: For specific tasks like reading odometer readings or license plates, Azure AI Vision v4.0 Read OCR capabilities can be used.

#### Damage Detection and Documentation

* Spacial Damage Mapping: To determine if dmamages exist, you would likely need a custom Vision model trained on annotated vehicle images. I imagine a lot of training data would be required to get good accuracy on damage detection.

* Measurement Extraction & Cost Estimation: Measurement extraction would be really tricky. Cost estimation could be 'roughly' done by feeding the results of the spacial damage mapping into a function that consults a knowledge base of repair costs. This knowledge base could be a database or Azure Cognitive Search index containing entries like: {Damage Type, Part, Severity -> Typical Repair Actions, Average Cost}. Basically, this would require a little RAG or a well-structured database of costs and parts.

#### Voice-to-Text Inspection System

* Multilingual Voice Recognition: Azure Speech Service provides robust speech-to-text capabilities, including support for multiple languages. You only need one speech endpoint to handle english and spanish. There is a "languageIdentification" parameter you can set. You can even use a custom model (via fine tuning in foundry) to improve accuracy for 'automotive-specific' terms.

#### Contextual Form Filling

* Contextual Form Filling: using the results from the multilingual voice recognition, you can use Azure AI Language (CLU) to extract entities and intents from the transcribed text. This will allow you to fill out structured forms based on the recognized automotive terms and conditions. Entities would include things like {Part: “windshield”, Condition: “cracked”, Measurement: “2 inches”}.
      * Alternatively, you could use an Azure OpenAI resource and do some prompt engineering to get the required structured output. This would be more flexible, but also more complex to set up and maintain (and unpredictable// less consistent).

* Form Population and Storage (not handled with traditional services): The structured data from CLU or GPT is then used to fill a predefined inspection form template. Suppose our form has fields like Part Inspected, Condition, Measurements/Notes. The application logic will take the parsed output and insert values into the form (which could be a database record or a PDF/HTML report).

---
### Using Azure AI Agents


#### Image Quality Assessment

Consider a multi-agent system. This could be some standalone and some concurent agents, or this could be a sequence of agents that work together to achieve the goal. For starters, you may build something like this:

```python
image_quality_agent = ChatCompletionAgent(
        name="ImageQualityInspector",
        instructions=(
            "You evaluate image quality based on blur, exposure, and lighting conditions. "
            "You invoke the VisionAnalysisTool to detect blur and exposure issues. "
            "For images requiring specific content validation, invoke OCRTool to ensure critical text (odometer, license plate) is readable. "
            "If an image fails quality checks, clearly explain why and mark it for retake."
        ),
        service=AzureChatCompletion(
            service_id="azure_chat_service",
            endpoint=os.getenv('OPENAI_ENDPOINT'),
            api_key=os.getenv('OPENAI_API_KEY'),
            deployment_name=os.getenv('VISION_ANALYSIS_MODEL')
        ),
        tools=[VisionAnalysisTool(), OCRTool()]
    )

    damage_detection_agent = ChatCompletionAgent(
        name="VehicleDamageDetector",
        instructions=(
            "You identify and classify vehicle damages such as scratches, dents, paint damage, and mechanical issues. "
            "Invoke CustomVisionDamageDetectionTool to detect and classify visible damages. "
            "You will map each detected damage onto the vehicle schematic using DamageMappingTool, clearly documenting the location, type, and severity of each issue."
        ),
        service=AzureChatCompletion(
            service_id="azure_chat_service",
            endpoint=os.getenv('OPENAI_ENDPOINT'),
            api_key=os.getenv('OPENAI_API_KEY'),
            deployment_name=os.getenv('CUSTOM_VISION_MODEL')
        ),
        tools=[CustomVisionDamageDetectionTool(), DamageMappingTool()]
    )

    repair_cost_agent = ChatCompletionAgent(
        name="RepairCostEstimator",
        instructions=(
            "Given a structured damage report from VehicleDamageDetector, you query the RepairCostDatabaseTool "
            "to retrieve repair cost estimates based on damage type, part affected, and severity. "
            "You clearly summarize estimated costs for each damage found."
        ),
        service=AzureChatCompletion(
            service_id="azure_chat_service",
            endpoint=os.getenv('OPENAI_ENDPOINT'),
            api_key=os.getenv('OPENAI_API_KEY'),
            deployment_name=os.getenv('GPT_MODEL')
        ),
        tools=[RepairCostDatabaseTool()]
    )

    reporting_agent = ChatCompletionAgent(
        name="InspectionReportGenerator",
        instructions=(
            "You compile outputs from ImageQualityInspector, VehicleDamageDetector, and RepairCostEstimator agents into a comprehensive inspection report. "
            "Your final report should include image quality scores, flagged images needing retakes, detailed damage documentation, spatial mapping, and repair cost estimations. "
            "Generate the report as structured JSON suitable for system ingestion, and provide a concise, human-readable summary as well."
        ),
        service=AzureChatCompletion(
            service_id="azure_chat_service",
            endpoint=os.getenv('OPENAI_ENDPOINT'),
            api_key=os.getenv('OPENAI_API_KEY'),
            deployment_name=os.getenv('GPT_MODEL')
        )
    )

```

#### Voice-to-Text Inspection System

Consider an architecture similar to:

```python

 multilingual_transcription_agent = ChatCompletionAgent(
        name="MultilingualTranscriber",
        instructions=(
            "You listen to real-time audio input in English or Spanish. "
            "Invoke SpeechToTextTool to convert audio to text, using the correct language model based on detected input language. "
            "Output high-accuracy text transcription in English. Aim for at least 95% accuracy on automotive terminology."
        ),
        service=AzureChatCompletion(
            service_id="azure_speech_service",
            endpoint=os.getenv('AZURE_SPEECH_ENDPOINT'),
            api_key=os.getenv('AZURE_SPEECH_API_KEY'),
            deployment_name=os.getenv('SPEECH_MODEL')
        ),
        tools=[SpeechToTextTool()]
    )

    form_entry_agent = ChatCompletionAgent(
        name="FormEntryExtractor",
        instructions=(
            "You analyze transcription text from MultilingualTranscriber. Extract structured inspection details using automotive-specific language. "
            "Invoke InspectionVocabularyTool to validate or normalize part names and conditions. "
            "Fill out structured form entries including Part, Condition, Measurements, and Notes. "
            "If you encounter ambiguous phrases or measurements, clearly document them as requiring clarification."
        ),
        service=AzureChatCompletion(
            service_id="azure_chat_service",
            endpoint=os.getenv('OPENAI_ENDPOINT'),
            api_key=os.getenv('OPENAI_API_KEY'),
            deployment_name=os.getenv('GPT_MODEL')
        ),
        tools=[InspectionVocabularyTool()]
    )

    clarification_agent = ChatCompletionAgent(
        name="InspectionClarifier",
        instructions=(
            "If the FormEntryExtractor marks any form fields as ambiguous or incomplete, "
            "you proactively formulate clarification questions to ask the inspector. "
            "Record inspector responses clearly and update form entries accordingly. "
            "Continue clarification until all form fields meet confidence thresholds or the inspector explicitly marks them as complete."
        ),
        service=AzureChatCompletion(
            service_id="azure_chat_service",
            endpoint=os.getenv('OPENAI_ENDPOINT'),
            api_key=os.getenv('OPENAI_API_KEY'),
            deployment_name=os.getenv('GPT_MODEL')
        )
    )

    form_reporting_agent = ChatCompletionAgent(
        name="InspectionFormCompiler",
        instructions=(
            "You collect fully validated form data from FormEntryExtractor and InspectionClarifier. "
            "Compile finalized structured inspection form entries based on the JSON schema templates. "
            "Highlight fields that required clarification or manual inspector validation. "
            "Output a complete, structured JSON inspection form and a concise summary report for manual review."
        ),
        service=AzureChatCompletion(
            service_id="azure_chat_service",
            endpoint=os.getenv('OPENAI_ENDPOINT'),
            api_key=os.getenv('OPENAI_API_KEY'),
            deployment_name=os.getenv('GPT_MODEL')
        )
    )
```

## Deployment/Pipeline (Outside Scope)

* A common architecture is event-driven: for example, when a new inspection image is uploaded to Azure Blob Storage, an Azure Event Grid can trigger an Azure Function to analyze the image. The function would orchestrate calls to various Cognitive Services and store results

* Because most of these services are API driven, you have a lot of flexibility in how you deploy and integrate them. You could use Azure Logic Apps, Azure Functions, a custom web application, or even a fullstack application's backend to handle the orchestration and user interface.
