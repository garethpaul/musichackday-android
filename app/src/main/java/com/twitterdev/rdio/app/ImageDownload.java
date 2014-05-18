package com.twitterdev.rdio.app;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.http.AndroidHttpClient;
import android.os.AsyncTask;
import android.util.Log;
import android.webkit.URLUtil;
import android.widget.ImageView;

import com.nostra13.universalimageloader.core.ImageLoader;
import com.nostra13.universalimageloader.core.ImageLoaderConfiguration;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.HttpStatus;
import org.apache.http.client.methods.HttpGet;

import java.net.URL;
import java.net.URLConnection;

import java.io.InputStream;
import java.lang.ref.WeakReference;

/**
 * Created by gjones on 5/18/14.
 */

public class ImageDownload extends AsyncTask<String, Void, Bitmap> {
    //FeedItem feed;
    private final WeakReference<ImageView> imageViewReference;
    ImageLoader il = ImageLoader.getInstance();
    String url;

    public ImageDownload(ImageView imageView) {
        imageViewReference = new WeakReference<ImageView>(imageView);
    }

    @Override
    // Actual download method, run in the task thread
    protected Bitmap doInBackground(String... params) {
        // params comes from the execute() call: params[0] is the url.

        url = params[0];

        return null;
        //return //downloadBitmap(params[0]);
    }

    @Override
    // Once the image is downloaded, associates it to the imageView
    protected void onPostExecute(Bitmap bitmap) {
        il.displayImage(url, imageViewReference.get());

    }


}
