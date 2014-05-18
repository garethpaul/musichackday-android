package com.twitterdev.rdio.app;

/*
 Copyright (c) 2011 Rdio Inc

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.
 */


        import java.io.BufferedInputStream;
        import java.io.IOException;
        import java.io.InputStream;
        import java.net.URL;
        import java.net.URLConnection;
        import java.util.ArrayList;
        import java.util.Iterator;
        import java.util.LinkedList;
        import java.util.List;
        import java.util.Queue;

        import org.apache.http.NameValuePair;
        import org.apache.http.message.BasicNameValuePair;
        import org.json.JSONArray;
        import org.json.JSONException;
        import org.json.JSONObject;

        import com.nostra13.universalimageloader.core.ImageLoader;
        import com.nostra13.universalimageloader.core.ImageLoaderConfiguration;
        import com.rdio.android.api.Rdio;
        import com.rdio.android.api.RdioApiCallback;
        import com.rdio.android.api.RdioListener;
        import com.rdio.android.api.services.RdioAuthorisationException;
        import com.rdio.android.api.OAuth1WebViewActivity;

        import android.app.Activity;
        import android.app.DialogFragment;
        import android.content.Intent;
        import android.content.SharedPreferences;
        import android.content.SharedPreferences.Editor;
        import android.graphics.Bitmap;
        import android.graphics.BitmapFactory;
        import android.media.MediaPlayer;
        import android.media.MediaPlayer.OnCompletionListener;
        import android.net.Uri;
        import android.os.AsyncTask;
        import android.os.Bundle;
        import android.util.DisplayMetrics;
        import android.util.Log;
        import android.view.View;
        import android.view.View.OnClickListener;
        import android.view.Window;
        import android.view.WindowManager;
        import android.widget.ArrayAdapter;
        import android.widget.ImageView;
        import android.widget.ListView;
        import android.widget.TextView;
        import android.widget.Toast;

        import twitter4j.Query;
        import twitter4j.QueryResult;
        import twitter4j.Status;
        import twitter4j.Trend;
        import twitter4j.Trends;
        import twitter4j.Twitter;
        import twitter4j.TwitterException;
        import twitter4j.TwitterFactory;
        import twitter4j.auth.AccessToken;
        import twitter4j.auth.RequestToken;
        import twitter4j.conf.ConfigurationBuilder;

/**
 * Really basic test app for the Rdio playback API.
 */
public class RdioApp extends Activity implements RdioListener {

    private static SharedPreferences mSharedPreferences;
    private static Twitter twitter;
    private static RequestToken requestToken;
    private AccessToken twitterAccessToken;

    private static final String TAG = "RdioAPIExample";

    private MediaPlayer player;

    private Queue<Track> trackQueue;

    private static Rdio rdio;

    // TODO CHANGE THIS TO YOUR APPLICATION KEY AND SECRET

    private static final List<String> where = new ArrayList<String>();

    private static String accessToken = null;
    private static String accessTokenSecret = null;
    protected ImageLoader imageLoader;

    private static final String PREF_ACCESSTOKEN = "prefs.accesstoken";
    private static final String PREF_ACCESSTOKENSECRET = "prefs.accesstokensecret";

    private static String collectionKey = null;

    private ImageView albumArt;
    private ImageView playPause;

    private DialogFragment getUserDialog;
    private DialogFragment getCollectionDialog;
    private DialogFragment getHeavyRotationDialog;
    private ArrayAdapter<String> stringTweetAdapter;
    private List<twitter4j.Status> statuses;
    private List<String> stringStatuses = new ArrayList<String>();
    private Activity ac;

    // Our model for the metadata for a track that we care about
    private class Track {
        public String key;
        public String trackName;
        public String artistName;
        public String albumName;
        public String albumArt;

        public Track(String k, String name, String artist, String album, String uri) {
            key = k;
            trackName = name;
            artistName = artist;
            albumName = album;
            albumArt = uri;
        }
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        //
        imageLoader = ImageLoader.getInstance();
        imageLoader.init(ImageLoaderConfiguration.createDefault(this));
        // set full screen
        requestWindowFeature(Window.FEATURE_NO_TITLE);

        final Activity ac = this;
        setContentView(R.layout.activity_main);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,
                WindowManager.LayoutParams.FLAG_FULLSCREEN);
        List<String> where = new ArrayList<String>();

        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);

        trackQueue = new LinkedList<Track>();

        // Initialize our Rdio object.  If we have cached access credentials, then use them - otherwise
        // Initialize w/ null values and the user will be prompted (if the Rdio app is installed), or
        // we'll fallback to 30s samples.
        if (rdio == null) {
            SharedPreferences settings = getPreferences(MODE_PRIVATE);
            accessToken = settings.getString(PREF_ACCESSTOKEN, null);
            accessTokenSecret = settings.getString(PREF_ACCESSTOKENSECRET, null);

            rdio = new Rdio(Constants.appKey, Constants.appSecret, accessToken, accessTokenSecret, this, this);

            if (accessToken == null || accessTokenSecret == null) {
                // If either one is null, reset both of them
                accessToken = accessTokenSecret = null;
                Intent myIntent = new Intent(RdioApp.this,
                        OAuth1WebViewActivity.class);
                myIntent.putExtra(OAuth1WebViewActivity.EXTRA_CONSUMER_KEY, Constants.appKey);
                myIntent.putExtra(OAuth1WebViewActivity.EXTRA_CONSUMER_SECRET, Constants.appSecret);
                RdioApp.this.startActivityForResult(myIntent, 1);

            } else {
                Log.d(TAG, "Found cached credentials:");
                Log.d(TAG, "Access token: " + accessToken);
                Log.d(TAG, "Access token secret: " + accessTokenSecret);
                rdio.prepareForPlayback();
            }

        }

        ImageView i = (ImageView)findViewById(R.id.next);
        i.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View v) {
                next(true);
            }
        });

        playPause = (ImageView)findViewById(R.id.playPause);
        playPause.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View v) {
                playPause();
            }
        });

        albumArt = (ImageView)findViewById(R.id.albumArt);
        playPause();
    }

    @Override
    public void onDestroy() {
        Log.i(TAG, "Cleaning up..");

        // Make sure to call the cleanup method on the API object
        rdio.cleanup();

        // If we allocated a player, then cleanup after it
        if (player != null) {
            player.reset();
            player.release();
            player = null;
        }

        super.onDestroy();
    }



    /**
     * Get the current user, and load their collection to start playback with.
     * Requires authorization and the Rdio app to be installed.
     */

    private void LoadMoreTracks() {
        if (accessToken == null || accessTokenSecret == null) {
            Log.i(TAG, "Anonymous user! No more tracks to play.");

            // Notify the user we're out of tracks
            //Toast.makeText(this, getString(R.string.no_more_tracks), Toast.LENGTH_LONG).show();

            // Then helpfully point them to the market to go install Rdio ;)
            accessToken = accessTokenSecret = null;
            Intent myIntent = new Intent(RdioApp.this,
                    OAuth1WebViewActivity.class);
            myIntent.putExtra(OAuth1WebViewActivity.EXTRA_CONSUMER_KEY, Constants.appKey);
            myIntent.putExtra(OAuth1WebViewActivity.EXTRA_CONSUMER_SECRET, Constants.appSecret);
            RdioApp.this.startActivityForResult(myIntent, 1);

            //finish();
            return;
        }

        showGetCollectionDialog();
        List<NameValuePair> args = new LinkedList<NameValuePair>();

        //


        //args.add(new BasicNameValuePair("query", where.get(1)));
        args.add(new BasicNameValuePair("type", "Track"));
        //Log.v("args", args.toString());
        rdio.apiCall("getTopCharts", args, new RdioApiCallback() {
            @Override
            public void onApiFailure(String methodName, Exception e) {
                dismissGetCollectionDialog();
                Log.e(TAG, methodName + " failed: ", e);
            }

            @Override
            public void onApiSuccess(JSONObject result) {
                try {
                    Log.v("result", result.toString());
                    //result = result.getJSONObject("result");

//                    result = result.getJSONObject(collectionKey);
                    List<Track> trackKeys = new LinkedList<Track>();
                    JSONArray tracks = result.getJSONArray("result");
                    Log.v("results", tracks.toString());
                    for (int i=0; i<tracks.length(); i++) {
                        JSONObject trackObject = tracks.getJSONObject(i);
                        String key = trackObject.getString("key");
                        final String name = trackObject.getString("name");
                        final String artist = trackObject.getString("artist");
                        String album = trackObject.getString("album");
                        String albumArt = trackObject.getString("icon");
                        Log.d(TAG, "Found track: " + key + " => " + trackObject.getString("name"));

                        trackKeys.add(new Track(key, artist, album, name, albumArt));
                    }
                    if (trackKeys.size() > 1)
                        trackQueue.addAll(trackKeys);
                    dismissGetCollectionDialog();

                    next(true);

                } catch (Exception e) {
                    dismissGetCollectionDialog();
                    Log.e(TAG, "Failed to handle JSONObject: ");
                }
            }
        });
    }

    private void next(final boolean manualPlay) {
        if (player != null) {
            player.stop();
            player.release();
            player = null;
        }

        final Track track = trackQueue.poll();
        if (trackQueue.size() < 3) {
            Log.i(TAG, "Track queue depleted, loading more tracks");
            LoadMoreTracks();
        }

        if (track == null) {
            Log.e(TAG, "Track is null!  Size of queue: " + trackQueue.size());
            return;
        }

        // Load the next track in the background and prep the player (to start buffering)
        // Do this in a bkg thread so it doesn't block the main thread in .prepare()
        AsyncTask<Track, Void, Track> task = new AsyncTask<Track, Void, Track>() {
            @Override
            protected Track doInBackground(Track... params) {
                Track track = params[0];
                final String trackName = track.artistName;
                final String artist = track.trackName;
                try {
                    player = rdio.getPlayerForTrack(track.key, null, manualPlay);
                    player.prepare();
                    player.setOnCompletionListener(new OnCompletionListener() {
                        @Override
                        public void onCompletion(MediaPlayer mp) {
                            next(false);
                        }
                    });
                    player.start();
                    new getSearch().execute(track.trackName);
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            TextView a = (TextView) findViewById(R.id.artist);
                            //a.setText(artist);
                            TextView t = (TextView) findViewById(R.id.track);
                            //t.setText(trackName);
                        }
                    });

                } catch (Exception e) {
                    Log.e("Test", "Exception " + e);
                }
                return track;
            }

            @Override
            protected void onPostExecute(Track track) {
                updatePlayPause(true);
            }
        };
        task.execute(track);

        // Fetch album art in the background and then update the UI on the main thread
        AsyncTask<Track, Void, Bitmap> artworkTask = new AsyncTask<Track, Void, Bitmap>() {
            @Override
            protected Bitmap doInBackground(Track... params) {
                Track track = params[0];
                try {
                    String artworkUrl = track.albumArt.replace("square-200", "square-600");
                    Log.i(TAG, "Downloading album art: " + artworkUrl);
                    Bitmap bm = null;
                    try {
                        URL aURL = new URL(artworkUrl);
                        URLConnection conn = aURL.openConnection();
                        conn.connect();
                        InputStream is = conn.getInputStream();
                        BufferedInputStream bis = new BufferedInputStream(is);
                        bm = BitmapFactory.decodeStream(bis);
                        bis.close();
                        is.close();
                    } catch (IOException e) {
                        Log.e(TAG, "Error getting bitmap", e);
                    }
                    return bm;
                } catch (Exception e) {
                    Log.e(TAG, "Error downloading artwork", e);
                    return null;
                }
            }

            @Override
            protected void onPostExecute(Bitmap artwork) {
                if (artwork != null) {
                    int imageWidth = artwork.getWidth();
                    int imageHeight = artwork.getHeight();
                    DisplayMetrics dimension = new DisplayMetrics();
                    getWindowManager().getDefaultDisplay().getMetrics(dimension);
                    int newWidth = dimension.widthPixels;

                    float scaleFactor = (float)newWidth/(float)imageWidth;
                    int newHeight = (int)(imageHeight * scaleFactor);

                    artwork = Bitmap.createScaledBitmap(artwork, newWidth, newHeight, true);
                    //albumArt.setImageBitmap(bitmap);



                    albumArt.setAdjustViewBounds(true);
                    albumArt.setImageBitmap(artwork);

                } else
                    albumArt.setImageResource(R.drawable.blank_album_art);
            }
        };
        artworkTask.execute(track);



        //Toast.makeText(this, String.format(getResources().getString(R.string.now_playing), track.trackName, track.albumName, track.artistName), Toast.LENGTH_LONG).show();
    }

    private void playPause() {
        if (player != null) {
            if (player.isPlaying()) {
                player.pause();
                updatePlayPause(false);
            } else {
                player.start();
                updatePlayPause(true);
            }
        } else {
            next(true);
        }
    }

    private void updatePlayPause(boolean playing) {
        if (playing) {
            playPause.setImageResource(R.drawable.pause);
        } else {
            playPause.setImageResource(R.drawable.play);
        }
    }

    /*************************
     * RdioListener Interface
     *************************/

	/*
	 * Dispatched by the Rdio object when the Rdio object is done initializing, and a connection
	 * to the Rdio app service has been established.  If authorized is true, then we reused our
	 * existing OAuth credentials, and the API is ready for use.
	 * @see com.rdio.android.api.RdioListener#onRdioReady()
	 */
    @Override
    public void onRdioReadyForPlayback() {
        Log.i(TAG, "Rdio SDK is ready for playback");
    }

    @Override
    public void onRdioUserPlayingElsewhere() {
        Log.w(TAG, "Tell the user that playback is stopping.");
    }

    /*
     * Dispatched by the Rdio object once the setTokenAndSecret call has finished, and the credentials are
     * ready to be used to make API calls.  The token & token secret are passed in so that you can
     * save/cache them for future re-use.
     * @see com.rdio.android.api.RdioListener#onRdioAuthorised(java.lang.String, java.lang.String)
     */
    @Override
    public void onRdioAuthorised(String accessToken, String accessTokenSecret) {
        Log.i(TAG, "Application authorised, saving access token & secret.");
        Log.d(TAG, "Access token: " + accessToken);
        Log.d(TAG, "Access token secret: " + accessTokenSecret);

        SharedPreferences settings = getPreferences(MODE_PRIVATE);
        Editor editor = settings.edit();
        editor.putString(PREF_ACCESSTOKEN, accessToken);
        editor.putString(PREF_ACCESSTOKENSECRET, accessTokenSecret);
        editor.commit();
    }

    /*************************
     * Activity overrides
     *************************/
    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == 1) {
            if (resultCode == RESULT_OK) {
                Log.v(TAG, "Login success");
                if (data != null) {
                    accessToken = data.getStringExtra("token");
                    accessTokenSecret = data.getStringExtra("tokenSecret");
                    onRdioAuthorised(accessToken, accessTokenSecret);
                    rdio.setTokenAndSecret(accessToken, accessTokenSecret);
                }
            } else if (resultCode == RESULT_CANCELED) {
                if (data != null) {
                    String errorCode = data.getStringExtra(OAuth1WebViewActivity.EXTRA_ERROR_CODE);
                    String errorDescription = data.getStringExtra(OAuth1WebViewActivity.EXTRA_ERROR_DESCRIPTION);
                    Log.v(TAG, "ERROR: " + errorCode + " - " + errorDescription);
                }
                accessToken = null;
                accessTokenSecret = null;
            }
            rdio.prepareForPlayback();
        }
    }

    /*************************
     * Dialog helpers
     *************************/
    private void showGetUserDialog() {
        if (getUserDialog == null) {
            getUserDialog = new RdioProgress();
        }

        if (getUserDialog.isAdded()) {
            return;
        }

        Bundle args = new Bundle();
        args.putString("message", getResources().getString(R.string.getting_user));

        getUserDialog.setArguments(args);
        getUserDialog.show(getFragmentManager(), "getUserDialog");
    }

    private void dismissGetUserDialog() {
        if (getUserDialog != null) {
            getUserDialog.dismiss();
        }
    }

    private void showGetCollectionDialog() {
        if (getCollectionDialog == null) {
            getCollectionDialog = new RdioProgress();
        }

        if (getCollectionDialog.isAdded()) {
            return;
        }

        Bundle args = new Bundle();
        args.putString("message", getResources().getString(R.string.getting_collection));

        getCollectionDialog.setArguments(args);
        getCollectionDialog.show(getFragmentManager(), "getCollectionDialog");
    }

    private void dismissGetCollectionDialog() {
        if (getCollectionDialog != null) {
            getCollectionDialog.dismiss();
        }
    }

    private void showGetHeavyRotationDialog() {
        if (getHeavyRotationDialog == null) {
            getHeavyRotationDialog = new RdioProgress();
        }

        if (getHeavyRotationDialog.isAdded()) {
            return;
        }

        Bundle args = new Bundle();
        args.putString("message", getResources().getString(R.string.getting_heavy_rotation));

        getHeavyRotationDialog.setArguments(args);
        getHeavyRotationDialog.show(getFragmentManager(), "getHeavyRotationDialog");
    }

    private void dismissGetHeavyRotationDialog() {
        if (getHeavyRotationDialog != null) {
            getHeavyRotationDialog.dismiss();
        }
    }

    // Twitter info

    private class getSearch extends AsyncTask<String, Void, String> {

        // set the last_tweet this is displayed on the device in a TextView

        @Override
        protected String doInBackground(String... params) {

            Log.v("LoggedIn", "getUser..doInBackground");
            Log.v("Search for ", params[0]);
            ConfigurationBuilder builder = new ConfigurationBuilder();
            builder.setOAuthConsumerKey(Constants.API_KEY);
            builder.setOAuthConsumerSecret(Constants.API_SECRET);

            //
            final Activity ac = RdioApp.this;

            // // Setup preferences
            mSharedPreferences = getApplicationContext().getSharedPreferences(
                    "twitter4j-sample", 0);

            // Access Token
            String twitter_access_token = mSharedPreferences.getString(Constants.PREF_KEY_OAUTH_TOKEN, "");
            // Access Token Secret
            String twitter_access_token_secret = mSharedPreferences.getString(Constants.PREF_KEY_OAUTH_SECRET, "");
            // Setup Access Token
            AccessToken accessToken = new AccessToken(twitter_access_token, twitter_access_token_secret);
            // Setup instance of twitter to perform requests e.g. twitter.showUser(<:handle>);
            Twitter twitter = new TwitterFactory(builder.build()).getInstance(accessToken);
            // Define the twitter_handle
            Query query = new Query(params[0]);
            QueryResult result = null;
            try {
                result = twitter.search(query);
            } catch (TwitterException e) {
                e.printStackTrace();
            }


            final ArrayList<String> items = new ArrayList<String>();
            final JSONArray tweets = new JSONArray();
            for (twitter4j.Status status : result.getTweets()) {
                final twitter4j.Status s = status;
                JSONObject t = new JSONObject();
                try {
                    t.put("tweet", s.getText());
                    t.put("src", s.getUser().getBiggerProfileImageURL());
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                tweets.put(t);
                items.add(s.getText());

            }

            final ListView listView = (ListView) findViewById(R.id.list);
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    String[] array = items.toArray(new String[items.size()]);
                    //r

                    //TweetAdapter a = new TweetAdapter(ac,tweets);
                    TweetAdapter a = new TweetAdapter(ac, R.layout.list_v,tweets);
                    listView.setAdapter(a);

                }


            });



            // Try and make magic

            return null;
        }
    }

}
