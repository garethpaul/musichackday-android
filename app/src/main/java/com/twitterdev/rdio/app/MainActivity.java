package com.twitterdev.rdio.app;



import android.content.Intent;
        import android.content.SharedPreferences;
        import android.content.SharedPreferences.Editor;
        import android.net.Uri;
        import android.os.AsyncTask;
        import android.support.v7.app.ActionBarActivity;
        import android.os.Bundle;
        import android.util.Log;
        import android.view.Menu;
        import android.view.MenuItem;
        import android.view.View;
        import android.view.Window;
        import android.view.WindowManager;
import android.widget.ArrayAdapter;
import android.widget.ImageButton;
        import android.widget.ImageView;
        import android.widget.Toast;

import java.util.ArrayList;
import java.util.List;

import twitter4j.Status;
import twitter4j.Twitter;
        import twitter4j.TwitterFactory;
        import twitter4j.auth.AccessToken;
        import twitter4j.auth.RequestToken;
        import twitter4j.conf.Configuration;
        import twitter4j.conf.ConfigurationBuilder;

public class MainActivity extends ActionBarActivity {

    private static SharedPreferences mSharedPreferences;
    private static Twitter twitter;
    private static RequestToken requestToken;
    private AccessToken accessToken;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // set full screen
        requestWindowFeature(Window.FEATURE_NO_TITLE);

        setContentView(R.layout.activity_main);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,
                WindowManager.LayoutParams.FLAG_FULLSCREEN);
        ImageView imgV = (ImageView) findViewById(R.id.imageView);
        imgV.setScaleType(ImageView.ScaleType.FIT_XY);

        //
        mSharedPreferences = getApplicationContext().getSharedPreferences(
                "twitter4j-sample", 0);

        // handle on click
        ImageButton btnLoginTwitter = (ImageButton) findViewById(R.id.btnLogin);
        btnLoginTwitter.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View arg0) {
                // Call login twitter function
                loginToTwitter();
            }
        });

        // capture uri
        if (!isTwitterLoggedInAlready()) {
            Uri uri = getIntent().getData();
            if (uri != null && uri.toString().startsWith(Constants.CALLBACKURL)) {
                // oAuth verifier
                final String verifier = uri
                        .getQueryParameter(Constants.URL_TWITTER_OAUTH_VERIFIER);

                try {

                    Thread thread = new Thread(new Runnable(){
                        @Override
                        public void run() {
                            try {

                                // Get the access token
                                accessToken = twitter.getOAuthAccessToken(
                                        requestToken, verifier);
                                Log.v("accessToken", accessToken.getToken());
                                // Shared Preferences
                                mSharedPreferences = getApplicationContext().getSharedPreferences(
                                        "twitter4j-sample", 0);
                                Editor e = mSharedPreferences.edit();


                                // After getting access token, access token secret
                                // store them in application preferences
                                e.putString(Constants.PREF_KEY_OAUTH_TOKEN, accessToken.getToken());
                                e.putString(Constants.PREF_KEY_OAUTH_SECRET, accessToken.getTokenSecret());
                                // Store login status - true
                                e.putBoolean(Constants.PREF_KEY_TWITTER_LOGIN, true);
                                e.commit(); // save changes

                                Log.e("Twitter OAuth Token", "> " + accessToken.getToken());
                                Intent myIntent = new Intent(getBaseContext(), RdioApp.class);
                                startActivity(myIntent);

                                // Hide login button
                            } catch (Exception e) {
                                e.printStackTrace();
                            }
                        }
                    });
                    thread.start();



                } catch (Exception e) {
                    // Check log for login errors
                    Log.e("Twitter Login Error", "> " + e.getMessage());
                    e.printStackTrace();
                }
            }
        } else {
            Intent myIntent = new Intent(getBaseContext(), RdioApp.class);
            startActivity(myIntent);

        }
    }






    private boolean isTwitterLoggedInAlready() {
        // return twitter login status from Shared Preferences
        return mSharedPreferences.getBoolean(Constants.PREF_KEY_TWITTER_LOGIN, false);
    }


    private void loginToTwitter() {
        // Check if already logged in
        if (!isTwitterLoggedInAlready()) {
            // Setup builder
            ConfigurationBuilder builder = new ConfigurationBuilder();
            // Get key and secret from Constants.java
            builder.setOAuthConsumerKey(Constants.API_KEY);
            builder.setOAuthConsumerSecret(Constants.API_SECRET);

            // Build
            Configuration configuration = builder.build();
            TwitterFactory factory = new TwitterFactory(configuration);
            twitter = factory.getInstance();

            // Start new thread for activity (you can't do too much work on the UI/Main thread.
            Thread thread = new Thread(new Runnable(){
                @Override
                public void run() {
                    try {

                        requestToken = twitter
                                .getOAuthRequestToken(Constants.CALLBACKURL);
                        MainActivity.this.startActivity(new Intent(Intent.ACTION_VIEW, Uri
                                .parse(requestToken.getAuthenticationURL())));

                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            });
            thread.start();
        } else {
            Intent myIntent = new Intent(getBaseContext(), RdioApp.class);
            startActivity(myIntent);
        }
    }

}
