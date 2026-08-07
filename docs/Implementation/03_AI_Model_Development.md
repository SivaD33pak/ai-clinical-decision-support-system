# 03 - AI Model Development

> **Project:** AI Clinical Decision Support System (AI-CDSS)
>
> **Version:** 1.0
>
> **Document:** AI Model Development
>
> **Part:** 1
>
> **Status:** Development Specification

---

# Purpose

This document defines the complete Artificial Intelligence architecture for Version 1 of the AI Clinical Decision Support System.

Version 1 focuses exclusively on **Chest X-ray Disease Classification** using Deep Learning.

The goal of this phase is **not** to build a production-grade AI model with state-of-the-art accuracy. Instead, the goal is to create a reliable, explainable, and scalable AI module that integrates seamlessly with the backend architecture defined in **02_Backend_Foundation.md**.

This document serves as the implementation guide for all AI-related development.

---

# Objectives

By the end of the AI Development phase, the system should:

- Train a Chest X-ray disease classification model
- Export the trained model
- Support inference through the Inference Manager
- Produce prediction confidence scores
- Support Explainable AI (Grad-CAM) in later phases
- Be easily replaceable or extendable with future AI models

Version 1 will only support Chest X-ray prediction.

Future versions will add:

- Blood Report Analysis
- Symptom Analysis
- Multimodal AI
- Clinical Decision Fusion

---

# AI Design Principles

The AI system follows the following principles.

---

# 1. AI is Independent of the Backend

The backend should never know how the AI model works.

Instead

```
Prediction Service

↓

Inference Manager

↓

AI Model

↓

Prediction Result
```

The backend only requests a prediction.

The AI decides how the prediction is generated.

---

# 2. AI is Replaceable

The Prediction Service should never depend on DenseNet121 directly.

Current

```
Prediction

↓

DenseNet121
```

Future

```
Prediction

↓

Vision Transformer

↓

DenseNet201

↓

EfficientNet

↓

Multimodal Model
```

Changing the AI model should require no backend modifications.

---

# 3. Modular AI

Each AI responsibility belongs to its own module.

```
AI

↓

Preprocessing

↓

Inference

↓

Explainability

↓

Model
```

Every component should be replaceable independently.

---

# AI System Overview

```
                 Chest X-ray

                      │

                      ▼

              Image Validation

                      │

                      ▼

              Image Preprocessing

                      │

                      ▼

               DenseNet121

                      │

                      ▼

             Disease Prediction

                      │

                      ▼

            Confidence Score

                      │

                      ▼

           Prediction Response
```

Future

```
Chest X-ray

Blood Report

Symptoms

↓

Inference Manager

↓

Multimodal AI

↓

Clinical Prediction
```

---

# AI Folder Structure

The AI module follows a modular architecture.

```
backend/

app/

ai/

│

├── datasets/

│

├── preprocessing/

│

├── augmentation/

│

├── inference/

│

├── training/

│

├── evaluation/

│

├── explainability/

│

├── models/

│   ├── xray/
│   ├── blood/
│   └── multimodal/

│

├── utils/

│

└── exports/
```

Every folder owns one responsibility.

---

# Folder Responsibilities

## datasets/

Stores dataset metadata and helper scripts.

No model code.

---

## preprocessing/

Responsible for preparing images before training or inference.

Tasks include

- Resize
- Normalize
- Convert Tensor
- Standardization

---

## augmentation/

Responsible for increasing dataset diversity.

Examples

- Random Rotation
- Horizontal Flip
- Brightness Adjustment
- Random Crop

Augmentation is used only during training.

---

## training/

Contains training logic.

Responsibilities

- Training Loop
- Validation Loop
- Checkpoint Saving
- Early Stopping

---

## evaluation/

Responsible for evaluating trained models.

Metrics

- Accuracy
- Precision
- Recall
- F1 Score
- Confusion Matrix

---

## inference/

Responsible for model inference.

No training logic.

---

## explainability/

Responsible for Explainable AI.

Future

- Grad-CAM
- Heatmap Generation

---

## exports/

Stores exported models.

Examples

```
xray_model.pth

best_model.pth
```

---

# Problem Definition

The AI model solves a supervised image classification problem.

Input

```
Chest X-ray Image
```

Output

```
Disease Class
```

Example

```
Input

↓

Chest X-ray

↓

Output

↓

Pneumonia

↓

Confidence

96.3%
```

---

# Why Deep Learning?

Traditional Machine Learning requires manually extracting image features.

Examples

- Edge Detection
- Texture Extraction
- Shape Features

Medical images are too complex for manual feature engineering.

Deep Learning automatically learns visual features directly from images.

---

# Why Convolutional Neural Networks?

Chest X-rays are images.

CNNs are specifically designed to process images.

CNNs learn

- Edges
- Shapes
- Texture
- Anatomical Structures

without manual programming.

---

# Why Transfer Learning?

Training a CNN from scratch requires millions of images.

Medical datasets are relatively small.

Transfer Learning solves this problem.

Instead of training from zero

```
Random Network

↓

Train

Millions of Images
```

We begin with

```
Pretrained DenseNet121

↓

Fine Tune

Chest X-ray Dataset
```

Benefits

- Faster training
- Better accuracy
- Less overfitting
- Lower hardware requirements

---

# Why DenseNet121?

Version 1 uses DenseNet121.

Reasons

- Excellent performance on Chest X-rays
- Proven in medical imaging research
- Moderate GPU requirements
- Widely supported in PyTorch
- Easier to fine-tune than larger models

Alternative models considered

- ResNet50
- EfficientNet
- Vision Transformer

DenseNet121 provides the best balance between accuracy, speed, and implementation complexity for this project.

---

# Dataset Selection

Version 1 requires a labeled Chest X-ray dataset.

Selection criteria

- Publicly available
- Balanced classes where possible
- Research-grade quality
- Suitable for transfer learning
- Compatible with academic use

Recommended datasets

Primary

```
Chest X-ray Images (Pneumonia)

Kaggle
```

Alternative

```
NIH ChestX-ray14
```

Advanced

```
CheXpert
```

For this project, use **only one dataset** to keep the implementation manageable.

---

# Dataset Organization

The dataset should follow this structure.

```
datasets/

chest_xray/

train/

NORMAL/

PNEUMONIA/

validation/

NORMAL/

PNEUMONIA/

test/

NORMAL/

PNEUMONIA/
```

Every image must belong to exactly one class.

---

# Dataset Verification

Before training, verify

- Images are readable
- Labels are correct
- No duplicate files
- No corrupted images
- Expected folder structure
- Class distribution

Training should never begin before dataset verification.

---

# Image Preprocessing

Every image must undergo preprocessing before reaching the model.

Pipeline

```
Image

↓

Read

↓

Resize

↓

Convert RGB

↓

Normalize

↓

Convert Tensor

↓

Ready
```

Training and inference must use the same preprocessing pipeline.

---

# Image Size

Version 1 uses

```
224 × 224
```

Reason

DenseNet121 expects 224×224 images.

Changing image size requires retraining.

---

# Color Channels

Although Chest X-rays appear grayscale, they should be converted to the format expected by the pretrained DenseNet121 model.

Maintain a consistent preprocessing pipeline for both training and inference.

---

# Data Normalization

Normalization ensures pixel values are in a range suitable for training.

This improves

- Training stability
- Convergence
- Model performance

Normalization must be identical during training and inference.

---

# Data Augmentation

Augmentation increases training diversity.

Recommended augmentations

- Random Horizontal Flip
- Random Rotation (small angles)
- Random Brightness Adjustment

Avoid unrealistic transformations such as vertical flips or extreme rotations, as they may produce medically implausible images.

Augmentation is applied only to the training dataset.

Validation and test datasets should remain unchanged.

---

# Definition of Done

Part 1 is complete when:

- [ ] AI folder structure created
- [ ] Dataset selected
- [ ] Dataset downloaded
- [ ] Dataset organized
- [ ] Dataset verified
- [ ] Preprocessing pipeline defined
- [ ] Augmentation strategy defined
- [ ] Image dimensions decided
- [ ] Transfer Learning strategy selected
- [ ] DenseNet121 selected
- [ ] AI architecture documented

No model training should occur during this part.

The objective is to establish a robust AI foundation before implementation.

---

# Next Part

Part 2 will implement:

- DenseNet121 Architecture
- PyTorch Project Structure
- Custom Dataset Class
- DataLoader
- Training Pipeline
- Transfer Learning
- Optimizer
- Loss Function
- Learning Rate Scheduler
- Model Checkpointing

# 03 - AI Model Development

> **Project:** AI Clinical Decision Support System (AI-CDSS)
>
> **Version:** 1.0
>
> **Document:** AI Model Development
>
> **Part:** 2
>
> **Status:** Development Specification

---

# Purpose

This document defines the complete model training pipeline for Version 1 of the AI Clinical Decision Support System.

The objective is to build a reproducible and maintainable deep learning training pipeline using PyTorch and Transfer Learning.

This document does not focus on backend integration. It focuses entirely on building the AI model.

---

# Objectives

At the end of this phase the AI module should:

- Load the Chest X-ray dataset
- Build a custom PyTorch Dataset
- Create DataLoaders
- Load DenseNet121
- Configure Transfer Learning
- Train the model
- Validate the model
- Save checkpoints
- Export the best model

---

# AI Training Pipeline

Every training run follows this workflow.

```
Dataset

↓

Dataset Verification

↓

Image Preprocessing

↓

Data Augmentation

↓

PyTorch Dataset

↓

DataLoader

↓

DenseNet121

↓

Forward Pass

↓

Loss Calculation

↓

Backpropagation

↓

Optimizer

↓

Validation

↓

Checkpoint Saving

↓

Export Model
```

---

# PyTorch Project Structure

The training module should use the following structure.

```
training/

│

├── train.py

├── validate.py

├── dataset.py

├── dataloader.py

├── model.py

├── optimizer.py

├── scheduler.py

├── checkpoint.py

├── metrics.py

└── config.py
```

Every file owns one responsibility.

---

# Custom Dataset

The project should use a custom Dataset class.

Responsibilities

- Read image path
- Load image
- Apply preprocessing
- Apply augmentation
- Return image tensor
- Return label

The Dataset should NOT

- Train models
- Calculate metrics
- Save predictions

---

# DataLoader

The DataLoader is responsible for batching data.

Responsibilities

- Shuffle training data
- Create mini-batches
- Load batches efficiently

Recommended

```
Training

Shuffle = True

Validation

Shuffle = False

Testing

Shuffle = False
```

---

# Why Mini-Batches?

Instead of training on the entire dataset at once

```
Dataset

↓

Model
```

Use

```
Dataset

↓

Mini Batch

↓

Model

↓

Repeat
```

Benefits

- Lower memory usage
- Faster convergence
- Better generalization

---

# Transfer Learning

Version 1 uses Transfer Learning.

Workflow

```
ImageNet

↓

DenseNet121

↓

Replace Classifier

↓

Fine Tune

↓

Chest X-ray Model
```

We do NOT train from scratch.

---

# DenseNet121

DenseNet121 consists of

- Initial Convolution
- Dense Blocks
- Transition Layers
- Global Average Pooling
- Classifier

Only the classifier should be replaced.

---

# Model Customization

Load pretrained DenseNet121.

Replace

```
Original Classifier
```

with

```
Custom Classifier
```

Output neurons must equal the number of disease classes.

Example

```
NORMAL

PNEUMONIA
```

↓

Output Size = 2

---

# Freeze Strategy

Initial training

Freeze

```
Feature Extractor
```

Train

```
Classifier
```

After classifier converges

Unfreeze

Upper Dense Blocks

↓

Fine Tune

This reduces overfitting.

---

# Forward Pass

Training iteration

```
Image

↓

DenseNet

↓

Prediction

↓

Loss
```

Forward pass calculates predictions.

No weights are updated yet.

---

# Loss Function

Version 1 uses

```
CrossEntropyLoss
```

Reason

Suitable for multi-class classification.

Benefits

- Stable
- Widely used
- Supported by PyTorch

---

# Optimizer

Recommended

```
AdamW
```

Reasons

- Better weight regularization
- Stable convergence
- Improved generalization

Alternative

```
Adam
```

Version 1 should prefer AdamW.

---

# Learning Rate

Recommended

```
0.0001
```

Learning rate should be configurable.

Never hardcode hyperparameters.

---

# Learning Rate Scheduler

Training should reduce the learning rate automatically.

Purpose

```
High Learning Rate

↓

Model Improves

↓

Lower Learning Rate

↓

Fine Tuning
```

This helps convergence.

---

# Epoch

One epoch

=

One complete pass through the training dataset.

Example

```
Dataset

↓

1000 Images

↓

Model Sees Every Image Once

↓

1 Epoch
```

---

# Batch Size

Recommended

```
16

or

32
```

Choose based on available GPU memory.

Batch size should remain configurable.

---

# Training Loop

Each epoch follows

```
Training Data

↓

Forward Pass

↓

Loss

↓

Backpropagation

↓

Optimizer Step

↓

Repeat

↓

Validation

↓

Metrics

↓

Checkpoint
```

---

# Backpropagation

Purpose

Adjust neural network weights.

Workflow

```
Prediction

↓

Loss

↓

Gradient Calculation

↓

Weight Update
```

This process repeats for every mini-batch.

---

# Validation Loop

Validation should occur

After every epoch.

Validation should NEVER

Update weights.

Purpose

Measure generalization.

---

# Early Stopping

Training should stop automatically if validation loss stops improving.

Benefits

- Prevent overfitting
- Save training time

---

# Checkpointing

Save model

Only when validation improves.

Never overwrite the best model unnecessarily.

Store

- Model weights
- Optimizer state
- Epoch
- Validation metrics

---

# Metrics During Training

Display

- Epoch
- Training Loss
- Validation Loss
- Training Accuracy
- Validation Accuracy

Training logs should be easy to read.

---

# Configuration File

Create

```
config.py
```

Store

- Learning Rate
- Batch Size
- Epochs
- Dataset Path
- Number of Classes
- Image Size

No training script should contain hardcoded values.

---

# Training Logs

Every epoch should log

```
Epoch

Training Loss

Validation Loss

Accuracy

Learning Rate

Time
```

Training progress should be reproducible.

---

# Model Export

Export only the best model.

Recommended location

```
exports/

best_model.pth
```

Future exports

```
TorchScript

ONNX
```

Version 1 exports only

```
.pth
```

---

# Coding Standards

The AI training module must follow these rules.

- One responsibility per file
- Configurable hyperparameters
- No hardcoded dataset paths
- No duplicated preprocessing
- Separate training and validation logic
- Separate metrics from training

---

# AI Coding Agent Tasks

The coding agent should implement the following.

## Dataset

- Custom Dataset class
- Image preprocessing
- Data augmentation

---

## Data Loading

- Training DataLoader
- Validation DataLoader
- Test DataLoader

---

## Model

- Load DenseNet121
- Replace classifier
- Freeze feature extractor
- Configure fine-tuning

---

## Training

- Forward pass
- Backpropagation
- Validation loop
- Early stopping
- Learning rate scheduler
- Checkpoint saving

---

## Export

- Save best model
- Save training logs

---

# Definition of Done

This phase is complete when:

- [ ] Dataset class implemented
- [ ] DataLoader implemented
- [ ] DenseNet121 loaded
- [ ] Classifier replaced
- [ ] Transfer learning configured
- [ ] Optimizer configured
- [ ] Scheduler configured
- [ ] Training loop implemented
- [ ] Validation loop implemented
- [ ] Early stopping implemented
- [ ] Checkpoint saving implemented
- [ ] Best model exported

No inference API should exist yet.

The output of this phase is a trained model (`best_model.pth`) and a reproducible training pipeline.

---

# Next Part

Part 3 will cover:

- Model Evaluation
- Confusion Matrix
- Precision
- Recall
- F1 Score
- ROC Curve
- Threshold Selection
- Explainability (Grad-CAM)
- Inference Pipeline
- Model Optimization
- Integration with the Inference Manager

# 03 - AI Model Development

> **Project:** AI Clinical Decision Support System (AI-CDSS)
>
> **Version:** 1.0
>
> **Document:** AI Model Development
>
> **Part:** 3
>
> **Status:** Development Specification

---

# Purpose

This document defines how the trained AI model is evaluated, validated, exported, optimized, and integrated into the backend.

After this phase, the AI model should be production-ready and accessible through the backend's Inference Manager.

This document also introduces Explainable AI (XAI), ensuring that predictions are transparent rather than functioning as a black box.

---

# Objectives

At the end of this phase the AI system should:

- Evaluate model performance
- Analyze classification metrics
- Export the best model
- Support inference
- Generate confidence scores
- Generate Grad-CAM heatmaps
- Integrate with the backend
- Be production ready

---

# AI Deployment Pipeline

The complete AI workflow is:

```
Dataset

↓

Training

↓

Validation

↓

Evaluation

↓

Best Model

↓

Model Export

↓

Inference Manager

↓

Backend

↓

Flutter
```

Every stage should be independently testable.

---

# Model Evaluation

A high accuracy alone does not indicate a good medical model.

Medical AI requires multiple evaluation metrics.

Every trained model should be evaluated using

- Accuracy
- Precision
- Recall
- F1 Score
- Confusion Matrix

Optional

- ROC Curve
- AUC Score

---

# Accuracy

Definition

```
Correct Predictions

──────────────────────

Total Predictions
```

Measures

Overall correctness.

Limitation

Accuracy may be misleading if classes are imbalanced.

Example

```
98%

Accuracy
```

does not necessarily mean the model performs well.

---

# Precision

Definition

```
Correct Positive Predictions

────────────────────────────

All Positive Predictions
```

Measures

How reliable positive predictions are.

High precision

↓

Few False Positives

Important in medical diagnosis.

---

# Recall

Definition

```
Correct Positive Predictions

────────────────────────────

Actual Positive Cases
```

Measures

How many actual disease cases were detected.

High Recall

↓

Few False Negatives

Medical AI should prioritize Recall over Accuracy.

---

# F1 Score

Definition

Harmonic Mean

↓

Precision

↓

Recall

Purpose

Provide balanced evaluation.

Version 1 should report

- Accuracy
- Precision
- Recall
- F1 Score

for every experiment.

---

# Confusion Matrix

Every training run should generate a confusion matrix.

Example

```
                Predicted

             Normal Pneumonia

Actual

Normal      150       8

Pneumonia    10      180
```

Purpose

Understand

- False Positives

- False Negatives

---

# False Positives

Healthy patient

↓

Predicted Disease

Unnecessary medical concern.

---

# False Negatives

Diseased patient

↓

Predicted Healthy

Most dangerous outcome.

The project should aim to minimize False Negatives.

---

# Model Selection

Never choose the last trained model.

Always choose

```
Best Validation Performance
```

Criteria

1. Lowest Validation Loss

2. Highest F1 Score

3. Stable Recall

The selected model becomes

```
best_model.pth
```

---

# Model Export

Only export

```
best_model.pth
```

Location

```
data/

models/

best_model.pth
```

The backend should never load temporary checkpoints.

---

# Model Metadata

Every exported model should include metadata.

Recommended

```
Model Name

Version

Training Date

Dataset

Number of Classes

Input Size

Framework Version

Metrics
```

This makes future model management easier.

---

# Inference Pipeline

Inference differs from training.

Training

```
Image

↓

Forward Pass

↓

Backpropagation

↓

Weight Update
```

Inference

```
Image

↓

Preprocessing

↓

Forward Pass

↓

Prediction

↓

Confidence

↓

Return
```

No gradients should be calculated during inference.

---

# Prediction Pipeline

```
Uploaded Image

↓

Validation

↓

Resize

↓

Normalization

↓

Tensor Conversion

↓

DenseNet

↓

Softmax

↓

Prediction

↓

Confidence

↓

Return
```

Training preprocessing and inference preprocessing must be identical.

---

# Confidence Score

The model should return

```
Disease

Confidence
```

Example

```
Prediction

Pneumonia

Confidence

96.42%
```

Confidence is NOT a guarantee.

It represents the model's certainty.

---

# Explainable AI (XAI)

Medical AI should not behave as a black box.

Version 1 uses

```
Grad-CAM
```

Purpose

Visualize which parts of the X-ray influenced the prediction.

Workflow

```
Prediction

↓

Grad-CAM

↓

Heatmap

↓

Overlay

↓

Flutter
```

---

# Why Grad-CAM?

Benefits

- Improves trust
- Easier debugging
- Better demonstrations
- Better project presentation

Users can visually inspect why the AI predicted a disease.

---

# Heatmap Generation

Pipeline

```
Prediction

↓

Last Convolution Layer

↓

Activation Maps

↓

Gradients

↓

Heatmap

↓

Overlay Image

↓

Return
```

The heatmap should be generated after prediction.

---

# Explainability Folder

```
explainability/

│

├── gradcam.py

├── heatmap.py

└── overlay.py
```

Each file owns one responsibility.

---

# Backend Integration

The backend never communicates directly with DenseNet.

Instead

```
Prediction Service

↓

Inference Manager

↓

DenseNet

↓

Prediction

↓

Grad-CAM

↓

Return
```

The backend receives only

```
Prediction Result
```

---

# Prediction Result Structure

The AI module should return a standardized object.

Contents

- Disease
- Confidence
- Heatmap Path (Future)
- Prediction Time
- Model Version

No backend-specific information.

---

# Model Versioning

Every exported model should have a version.

Example

```
Version

1.0.0
```

Future

```
1.1.0

2.0.0
```

This prevents accidental deployment of incorrect models.

---

# AI Performance Optimization

Recommended

- Load model once
- Disable gradients during inference
- Cache preprocessing objects
- Avoid repeated disk access

Inference should be as lightweight as possible.

---

# AI Error Handling

Possible errors

- Invalid Image
- Corrupted Image
- Missing Model
- Unsupported Format
- Prediction Failure

Every error should produce meaningful responses.

---

# Testing Strategy

Testing should occur in stages.

---

## Unit Testing

Test

- Preprocessing
- Dataset
- Prediction
- Metrics

---

## Integration Testing

Test

- Inference Manager
- Model Loading
- Backend Integration

---

## End-to-End Testing

Flutter

↓

Backend

↓

Inference Manager

↓

Model

↓

Prediction

↓

Flutter

Complete pipeline should succeed.

---

# AI Coding Agent Tasks

The coding agent should implement

## Evaluation

- Accuracy
- Precision
- Recall
- F1 Score
- Confusion Matrix

---

## Model Export

- Save best model
- Save metadata

---

## Inference

- Prediction pipeline
- Confidence calculation
- Softmax output

---

## Explainability

- Grad-CAM
- Heatmap generation
- Overlay image

---

## Backend Integration

- Connect Inference Manager
- Return standardized prediction object

---

# Production Readiness Checklist

Before AI integration is complete verify

- [ ] Model trained
- [ ] Validation completed
- [ ] Metrics generated
- [ ] Confusion Matrix generated
- [ ] Best model exported
- [ ] Metadata generated
- [ ] Inference pipeline working
- [ ] Confidence scores returned
- [ ] Grad-CAM implemented
- [ ] Backend integration complete
- [ ] End-to-end prediction working

---

# AI Milestone

The AI module is considered complete when:

- The model successfully classifies Chest X-ray images.
- Predictions include confidence scores.
- Grad-CAM heatmaps are generated.
- The backend can request predictions through the Inference Manager.
- Flutter receives predictions without knowing how the AI model works.

At this stage, Version 1 of the AI Clinical Decision Support System is fully functional.

---

# Next Phase

**04 - Flutter Frontend Development**

The next phase focuses on:

- Authentication UI
- Dashboard
- Prediction Screen
- Image Upload
- Results Screen
- History Screen
- API Integration
- Error Handling
- Loading States
- Production-ready UI/UX

# 03 - AI Model Development

> **Project:** AI Clinical Decision Support System (AI-CDSS)
>
> **Version:** 1.0
>
> **Document:** AI Model Development
>
> **Part:** 4
>
> **Status:** Deployment & Integration Specification

---

# Purpose

This document defines how the trained AI model is deployed, managed, integrated with the backend, monitored, and prepared for future expansion.

Unlike previous parts, this phase focuses on **AI Serving** rather than **AI Training**.

The AI model should now become a reusable service that can be called by the backend through the Inference Manager.

---

# Objectives

By the end of this phase the AI module should:

- Load the trained model
- Serve predictions
- Integrate with the backend
- Generate explainable outputs
- Handle inference failures
- Support future AI models
- Be production-ready

---

# AI Serving Architecture

The deployed AI system follows this architecture.

```
Flutter

↓

FastAPI

↓

Prediction Router

↓

Prediction Service

↓

Inference Manager

↓

Model Registry

↓

DenseNet121

↓

Prediction Result

↓

Flutter
```

Business logic never communicates directly with the AI model.

---

# AI Serving Folder Structure

```
ai_core/

│

├── serving/

│   ├── inference_manager.py
│   ├── predictor.py
│   ├── preprocessing.py
│   ├── postprocessing.py
│   └── model_loader.py

│

├── models/

│   ├── xray/
│   ├── blood/
│   └── multimodal/

│

├── explainability/

│   ├── gradcam.py
│   ├── overlay.py
│   └── heatmap.py

│

├── evaluation/

│

├── training/

│

└── exports/

        best_model.pth
```

---

# Inference Manager

The Inference Manager is the only component responsible for AI orchestration.

Responsibilities

- Receive prediction request
- Select appropriate model
- Execute inference
- Return standardized response

The backend should never instantiate AI models directly.

---

# Model Registry

Purpose

Maintain a registry of all available AI models.

Current

```
DenseNet121
```

Future

```
DenseNet121

Blood CNN

Vision Transformer

Multimodal Model
```

The registry allows models to be replaced without changing application logic.

---

# Model Loader

Purpose

Load trained models into memory.

Responsibilities

- Load best_model.pth
- Validate model version
- Verify model compatibility
- Prepare model for inference

The model should be loaded only once during application startup.

Never reload the model for every prediction request.

---

# Prediction Pipeline

Every prediction follows this sequence.

```
Image Upload

↓

Validation

↓

Preprocessing

↓

Tensor Conversion

↓

Inference Manager

↓

Model

↓

Softmax

↓

Prediction

↓

Confidence Score

↓

Grad-CAM

↓

Prediction Result
```

---

# Standard Prediction Object

The AI layer should return a standardized object.

Fields

```
Prediction

Confidence

Class Index

Inference Time

Model Version

Heatmap Path (optional)

Prediction ID
```

The backend should not need to interpret raw tensors.

---

# Preprocessing Pipeline

Training preprocessing and inference preprocessing must be identical.

Pipeline

```
Image

↓

Resize

↓

Normalize

↓

Tensor

↓

Batch Dimension

↓

Inference
```

Maintaining consistency prevents training-serving skew.

---

# Postprocessing

After inference

Responsibilities

- Convert logits to probabilities
- Select predicted class
- Calculate confidence
- Map class index to disease name

Return only meaningful values.

---

# Confidence Threshold

Predictions below a configurable confidence threshold should be flagged.

Example

```
Confidence

↓

58%

↓

Low Confidence Prediction
```

Future versions may display a warning to users.

---

# Explainability Pipeline

After prediction

```
Prediction

↓

Grad-CAM

↓

Activation Maps

↓

Heatmap

↓

Overlay

↓

Save

↓

Return URL
```

Heatmaps should be generated independently from prediction logic.

---

# Prediction Result

Example

```
Prediction

Pneumonia

Confidence

96.41%

Model

DenseNet121

Inference Time

0.18 seconds

Heatmap

heatmap_102.png
```

---

# Error Handling

Possible AI errors

- Model Missing
- Unsupported Image
- Corrupted Image
- Invalid Tensor
- Prediction Failure
- Grad-CAM Failure

Each error should return a standardized response.

Never expose internal AI exceptions.

---

# AI Performance

The AI service should be optimized for inference.

Recommendations

- Load model once
- Disable gradient calculations
- Reuse preprocessing objects
- Keep inference stateless
- Cache model in memory

---

# Resource Management

Memory

- One loaded model instance

CPU

- Minimize preprocessing overhead

GPU

- Use if available

Fallback

- CPU inference

The application should automatically detect available hardware.

---

# Backend Integration

The backend communicates only through the Inference Manager.

Flow

```
Prediction Router

↓

Prediction Service

↓

Inference Manager

↓

Prediction Result

↓

Prediction Repository

↓

Supabase

↓

Flutter
```

The backend should never import DenseNet directly.

---

# Logging

Every prediction should log

- Timestamp
- Prediction ID
- Model Version
- Inference Time
- Confidence
- Result

Do not log patient-identifiable information.

---

# Monitoring

Track

- Total Predictions
- Average Inference Time
- Failed Predictions
- Model Version
- Last Startup Time

These metrics are useful for debugging and future deployment.

---

# AI Testing Strategy

Test

## Model Loading

- Correct model loaded
- Invalid model detected

---

## Preprocessing

- Correct image size
- Correct normalization
- Invalid image handling

---

## Inference

- Valid prediction
- Confidence calculation
- Multiple predictions

---

## Explainability

- Heatmap generated
- Overlay image created

---

## Integration

Flutter

↓

Backend

↓

Inference Manager

↓

Model

↓

Prediction

↓

Database

↓

Flutter

Complete workflow should succeed.

---

# Security

The AI module should

- Validate uploaded images
- Reject unsupported formats
- Prevent oversized uploads
- Avoid exposing model internals

Future versions may include request rate limiting.

---

# Future Expansion

The architecture should support

```
Blood Report

↓

Inference Manager

↓

Blood Model
```

without modifying

- Prediction Router
- Prediction Service
- Repository

Only

- Register new model
- Add preprocessing
- Add postprocessing

---

# AI Coding Agent Tasks

The coding agent should implement

## Serving

- Model Loader
- Inference Manager
- Predictor
- Preprocessing
- Postprocessing

---

## Explainability

- Grad-CAM
- Heatmap generation
- Overlay creation

---

## Integration

- Connect Inference Manager to Prediction Service
- Return standardized prediction object

---

## Testing

- Model loading tests
- Prediction tests
- Integration tests
- Performance benchmarks

---

# Production Readiness Checklist

Before deploying Version 1

- [ ] Model loads successfully
- [ ] Inference pipeline complete
- [ ] Prediction object standardized
- [ ] Confidence scores validated
- [ ] Grad-CAM integrated
- [ ] Backend integration completed
- [ ] Logging enabled
- [ ] Error handling implemented
- [ ] Integration tests passing
- [ ] End-to-end workflow verified

---

# AI Milestone

The AI subsystem is complete when

- A trained DenseNet121 model is exported.
- The model is loaded automatically at startup.
- The backend requests predictions only through the Inference Manager.
- Predictions include confidence scores.
- Explainability is available through Grad-CAM.
- The prediction workflow is fully integrated with the backend.

At this point, Version 1 of the AI Clinical Decision Support System is capable of performing complete Chest X-ray disease prediction from the Flutter application.

---

# Next Phase

## 04 - Flutter Frontend Development

The next phase covers:

- Flutter project architecture
- VGV architecture integration
- Authentication flow
- Dashboard
- Image upload
- Prediction workflow
- Result visualization
- History
- API integration
- Error handling
- Loading states
- UI/UX polishing
- Responsive design
- State management
- Production-ready frontend