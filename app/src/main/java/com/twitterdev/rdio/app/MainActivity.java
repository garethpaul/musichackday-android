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
    private static boolean twitterCallbackExchangeInFlight;
    private AccessToken accessToken;
    private boolean twitterLoginInFlight;


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
            if (isTwitterCallback(uri)) {
                // oAuth verifier
                final String verifier = uri
                        .getQueryParameter(Constants.URL_TWITTER_OAUTH_VERIFIER);
                final String callbackToken = uri
                        .getQueryParameter(Constants.URL_TWITTER_OAUTH_TOKEN);

                if (!hasOAuthVerifier(verifier)
                        || twitter == null
                        || requestToken == null
                        || !matchesRequestToken(callbackToken, requestToken)) {
                    Toast.makeText(MainActivity.this, "Twitter login was not started on this device.", Toast.LENGTH_LONG).show();
                    return;
                }
                final Twitter callbackTwitter = twitter;
                final RequestToken callbackRequestToken = requestToken;
                if (twitterCallbackExchangeInFlight) {
                    return;
                }
                twitterCallbackExchangeInFlight = true;

                try {

                    Thread thread = new Thread(new Runnable(){
                        @Override
                        public void run() {
                            try {

                                // Get the access token
                                accessToken = callbackTwitter.getOAuthAccessToken(
                                        callbackRequestToken, verifier);
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
                                if (!e.commit()) {
                                    finishTwitterCallbackExchange();
                                    logTwitterLoginFailure("Credential persistence");
                                    return;
                                }

                                MainActivity.this.runOnUiThread(new Runnable() {
                                    @Override
                                    public void run() {
                                        twitterCallbackExchangeInFlight = false;
                                        Intent myIntent = new Intent(getBaseContext(), RdioApp.class);
                                        startActivity(myIntent);
                                    }
                                });

                                // Hide login button
                            } catch (Exception e) {
                                finishTwitterCallbackExchange();
                                logTwitterLoginFailure("Access token exchange");
                            }
                        }
                    });
                    thread.start();



                } catch (Exception e) {
                    finishTwitterCallbackExchange();
                    logTwitterLoginFailure("OAuth callback handling");
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

    private boolean isTwitterCallback(Uri uri) {
        if (uri == null) {
            return false;
        }

        Uri callbackUri = Uri.parse(Constants.CALLBACKURL);
        String expectedScheme = callbackUri.getScheme();
        String expectedAuthority = callbackUri.getAuthority();
        String expectedPath = normalizedPath(callbackUri);
        String actualPath = normalizedPath(uri);
        return expectedScheme != null
                && expectedAuthority != null
                && expectedScheme.equals(uri.getScheme())
                && expectedAuthority.equals(uri.getAuthority())
                && expectedPath.equals(actualPath);
    }

    private String normalizedPath(Uri uri) {
        String path = uri.getPath();
        return path == null ? "" : path;
    }

    private boolean hasOAuthVerifier(String verifier) {
        return verifier != null && verifier.trim().length() > 0;
    }

    private boolean matchesRequestToken(String callbackToken, RequestToken activeRequestToken) {
        if (callbackToken == null || activeRequestToken == null) {
            return false;
        }

        String expectedToken = activeRequestToken.getToken();
        return expectedToken != null && expectedToken.equals(callbackToken);
    }

    private void finishTwitterCallbackExchange() {
        MainActivity.this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                twitterCallbackExchangeInFlight = false;
            }
        });
    }

    private boolean isTrustedTwitterAuthenticationUri(Uri uri) {
        return uri != null
                && "https".equals(uri.getScheme())
                && "api.twitter.com".equals(uri.getHost())
                && uri.getPort() == -1
                && "/oauth/authenticate".equals(uri.getPath());
    }


    private void loginToTwitter() {
        // Check if already logged in
        if (!isTwitterLoggedInAlready()) {
            if (twitterCallbackExchangeInFlight || twitterLoginInFlight) {
                return;
            }
            twitterLoginInFlight = true;

            try {
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
                            final Uri authenticationUri = Uri.parse(requestToken.getAuthenticationURL());
                            if (!isTrustedTwitterAuthenticationUri(authenticationUri)) {
                                finishTwitterLoginAttempt();
                                logTwitterLoginFailure("Authorization URL validation");
                                return;
                            }
                            MainActivity.this.runOnUiThread(new Runnable() {
                                @Override
                                public void run() {
                                    twitterLoginInFlight = false;
                                    MainActivity.this.startActivity(new Intent(Intent.ACTION_VIEW, authenticationUri));
                                }
                            });

                        } catch (Exception e) {
                            finishTwitterLoginAttempt();
                            logTwitterLoginFailure("Request token creation");
                        }
                    }
                });
                thread.start();
            } catch (Exception e) {
                twitterLoginInFlight = false;
                logTwitterLoginFailure("Request token setup");
            }
        } else {
            Intent myIntent = new Intent(getBaseContext(), RdioApp.class);
            startActivity(myIntent);
        }
    }

    private void finishTwitterLoginAttempt() {
        MainActivity.this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                twitterLoginInFlight = false;
            }
        });
    }

    private void logTwitterLoginFailure(String action) {
        Log.e("Twitter Login Error", action + " failed");
    }

}
