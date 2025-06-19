#!/bin/bash

# Firebase & GCP Automated Setup Script
# This script automates as much as possible of Firebase/GCP setup

set -e

# Configuration
PROJECT_ID="${1:-my-firebase-project-$(date +%s)}"
PROJECT_NAME="${2:-My Firebase Project}"
BILLING_ACCOUNT="${3:-}" # Optional: your billing account ID
REGION="${4:-us-central1}"

echo "🚀 Starting Firebase/GCP Project Setup"
echo "Project ID: $PROJECT_ID"
echo "Project Name: $PROJECT_NAME"

# Check prerequisites
command -v gcloud >/dev/null 2>&1 || { echo "❌ gcloud CLI required but not installed."; exit 1; }
command -v firebase >/dev/null 2>&1 || { echo "❌ firebase CLI required but not installed."; exit 1; }

# Step 1: Create GCP Project
echo "📦 Creating GCP project..."
gcloud projects create "$PROJECT_ID" --name="$PROJECT_NAME" || echo "Project may already exist"

# Step 2: Set project
gcloud config set project "$PROJECT_ID"

# Step 3: Enable required APIs
echo "🔧 Enabling required APIs..."
APIS=(
    "firebase.googleapis.com"
    "firestore.googleapis.com"
    "firebaserules.googleapis.com"
    "firebasestorage.googleapis.com"
    "firebasedatabase.googleapis.com"
    "cloudfunctions.googleapis.com"
    "cloudbuild.googleapis.com"
    "cloudresourcemanager.googleapis.com"
    "iam.googleapis.com"
    "serviceusage.googleapis.com"
    "appengine.googleapis.com"
)

for api in "${APIS[@]}"; do
    echo "Enabling $api..."
    gcloud services enable "$api" --project="$PROJECT_ID"
done

# Step 4: Link billing account (if provided)
if [ -n "$BILLING_ACCOUNT" ]; then
    echo "💳 Linking billing account..."
    gcloud beta billing projects link "$PROJECT_ID" --billing-account="$BILLING_ACCOUNT"
else
    echo "⚠️  No billing account provided. Some features may be limited."
fi

# Step 5: Create App Engine app (required for some Firebase features)
echo "🌐 Creating App Engine app..."
gcloud app create --region="$REGION" --project="$PROJECT_ID" || echo "App Engine app may already exist"

# Step 6: Create default service account for Firebase
echo "👤 Setting up service accounts..."
gcloud iam service-accounts create firebase-admin \
    --display-name="Firebase Admin" \
    --project="$PROJECT_ID" || echo "Service account may already exist"

# Grant necessary roles
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:firebase-admin@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/firebase.admin"

# Step 7: Initialize Firebase project locally
echo "🔥 Initializing Firebase in current directory..."
cat > firebase.json << EOF
{
  "hosting": {
    "public": "public",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"]
  },
  "firestore": {
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  },
  "storage": {
    "rules": "storage.rules"
  },
  "functions": {
    "source": "functions"
  }
}
EOF

# Create basic security rules
cat > firestore.rules << EOF
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
EOF

cat > storage.rules << EOF
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /{allPaths=**} {
      allow read, write: if request.auth != null;
    }
  }
}
EOF

# Create basic Firestore indexes
cat > firestore.indexes.json << EOF
{
  "indexes": [],
  "fieldOverrides": []
}
EOF

# Create functions directory
mkdir -p functions
cd functions
npm init -y
npm install firebase-admin firebase-functions
cd ..

echo "✅ Automated setup complete!"
echo ""
echo "⚠️  MANUAL STEPS REQUIRED:"
echo "1. Go to https://console.firebase.google.com"
echo "2. Click 'Add project' and select existing GCP project: $PROJECT_ID"
echo "3. Complete the Firebase setup wizard"
echo "4. Configure Authentication providers in Firebase Console"
echo "5. Add your app (iOS/Android/Web) in Project Settings"
echo "6. Download and add configuration files (google-services.json, GoogleService-Info.plist, or firebaseConfig)"
echo ""
echo "📝 Next steps:"
echo "- Run 'firebase login' if not already logged in"
echo "- Run 'firebase use $PROJECT_ID' to select this project"
echo "- Run 'firebase deploy' to deploy your rules and functions"
echo ""
echo "🔑 To create admin credentials:"
echo "gcloud iam service-accounts keys create ./service-account-key.json \\"
echo "  --iam-account=firebase-admin@$PROJECT_ID.iam.gserviceaccount.com"