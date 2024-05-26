$APP = "servicer-web-server-app"
gcloud builds submit \
  --tag gcr.io/$GOOGLE_CLOUD_PROJECT/$APP
gcloud run deploy $APP \
  --image gcr.io/$GOOGLE_CLOUD_PROJECT/$APP \
  --platform managed \
  --region $LOCATION \
  --allow-unauthenticated \
  --max-instances=1