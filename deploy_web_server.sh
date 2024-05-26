APP_SERVER="servicer-web-server-app"
gcloud builds submit \
  --tag gcr.io/$GOOGLE_CLOUD_PROJECT/$APP_SERVER
gcloud run deploy $APP_SERVER \
  --image gcr.io/$GOOGLE_CLOUD_PROJECT/$APP_SERVER \
  --platform managed \
  --region $LOCATION \
  --allow-unauthenticated \
  --max-instances=1