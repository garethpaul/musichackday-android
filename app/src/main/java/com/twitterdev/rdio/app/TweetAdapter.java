package com.twitterdev.rdio.app;



import android.app.Activity;
        import android.content.Context;
import android.graphics.Bitmap;
import android.os.AsyncTask;
import android.util.Log;
import android.view.LayoutInflater;
        import android.view.View;
        import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.BaseAdapter;
        import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
        import android.support.v4.app.FragmentActivity;

import com.nostra13.universalimageloader.core.ImageLoader;

import org.json.JSONArray;
import org.json.JSONException;

import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;


import org.json.JSONObject;


public class TweetAdapter extends BaseAdapter {

    private Activity activity;
    Context context;
    JSONArray data;
    int layoutResourceId;
    CropHolder cropHolder;
    public ImageLoader il;
    public LayoutInflater layoutInflater;

    private static LayoutInflater inflater=null;

    static class CropHolder {

        TextView tweet;
        ImageView src;

    }
    public TweetAdapter(Context context, int layoutResourceId, JSONArray data) {

        //super(context, layoutResourceId);
        // TODO Auto-generated constructor stub

        this.context = context;
        this.data = data;
        this.layoutResourceId = layoutResourceId;
        this.cropHolder = null;
        layoutInflater = LayoutInflater.from(context);
    }

    public void updateResults(List[] results) {

        //Triggers the list update
        notifyDataSetChanged();
    }


    public int getCount() {
        return data.length();
    }

    public Object getItem(int position) {
        return position;
    }

    public long getItemId(int position) {
        return position;
    }



    @Override
    public View getView(int pos, View convertView, ViewGroup parent) {
        Log.d("Working", "works here 38");
        View row = convertView;
        JSONObject crop;
        try {
            Log.d("Pos", Integer.toString(pos));
            crop = (JSONObject) data.getJSONObject(pos);
            if (row == null) {
                //ImageView thumb_image=(ImageView)row.findViewById(R.id.); // thumb image
                LayoutInflater inflater = ((Activity) context)
                        .getLayoutInflater();
                row = inflater.inflate(layoutResourceId, parent, false);

                cropHolder = new CropHolder();
                cropHolder.tweet = (TextView) row
                        .findViewById(R.id.tweet);
                cropHolder.src = (ImageView) row
                        .findViewById(R.id.user_icon);
                row.setTag(cropHolder);


            } else {
                cropHolder = (CropHolder) row.getTag();

            }

            cropHolder.tweet.setText(crop.getString("tweet"));
            ImageView thumb = (ImageView) cropHolder.src;
            Log.v("url-download", crop.getString("src"));
            //imageLoader.displayImage(imageUri, imageView);
            new ImageDownload(thumb).execute(crop.getString("src"));

            //imageLoader.DisplayImage(crop.getString("src"), thumb);


        } catch (JSONException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }

        return row;
    }

}
