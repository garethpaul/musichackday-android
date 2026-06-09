package com.twitterdev.rdio.app;

import java.lang.ref.SoftReference;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import android.graphics.Bitmap;

public class MemoryCache {
    private Map<String, SoftReference<Bitmap>> cache=Collections.synchronizedMap(new HashMap<String, SoftReference<Bitmap>>());

    public Bitmap get(String id){
        SoftReference<Bitmap> ref=cache.get(id);
        if(ref==null)
            return null;
        Bitmap bitmap=ref.get();
        if(bitmap==null)
            cache.remove(id);
        return bitmap;
    }

    public void put(String id, Bitmap bitmap){
        if(id==null || bitmap==null)
            return;
        cache.put(id, new SoftReference<Bitmap>(bitmap));
    }

    public void clear() {
        cache.clear();
    }
}
