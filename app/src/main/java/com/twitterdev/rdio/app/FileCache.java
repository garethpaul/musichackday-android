package com.twitterdev.rdio.app;

import java.io.UnsupportedEncodingException;
import java.io.File;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

import android.content.Context;

public class FileCache {

    private File cacheDir;

    public FileCache(Context context){
        cacheDir = new File(context.getCacheDir(), "LazyList");
        if(!cacheDir.exists() && !cacheDir.mkdirs())
            cacheDir = context.getCacheDir();
    }

    public File getFile(String url){
        File f = new File(cacheDir, cacheFileName(url));
        return f;

    }

    private String cacheFileName(String url) {
        String value = url == null ? "" : url;
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] bytes = digest.digest(value.getBytes("UTF-8"));
            StringBuilder builder = new StringBuilder(bytes.length * 2);
            for (byte item : bytes) {
                builder.append(String.format("%02x", item & 0xff));
            }
            return builder.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-256 unavailable", e);
        } catch (UnsupportedEncodingException e) {
            throw new IllegalStateException("UTF-8 unavailable", e);
        }
    }

    public void clear(){
        File[] files=cacheDir.listFiles();
        if(files==null)
            return;
        for(File f:files)
            f.delete();
    }

}
