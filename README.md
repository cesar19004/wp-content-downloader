# Wordpress content downloader 

WordPress Content Downloader provides an easier way to download all files and media inside wp-content/uploads directory. It also tries to skip image thumbnails, so only original files are downloaded

\*\*This script only works if ``wp-content/uploads`` and their children directories are public and return the index of their content\*\*

## Usage

```bash
python3 main.py [wp-site_url]
```
## Custom thumbnails regex
You can change the regex to find thumbnails with specific suffix, the file will be skipped only if exists another file without the suffix

E.g. let's say we have an original image ``image.jpg`` and 3 modified versions \
``image-16x16.jpg``, ``image-e1676678024195.jpg`` and ``image-e1676678024195-10x10.jpg``\
\
To remove modified versions, the regexes to add and their order should be

```python
thumbnails_regex_list = [
    "-\d{1,4}x\d{1,4}$", #first remove files with suffix of img size
    "-e\d{13}$", # next remove files with hash suffix from the remaining files
]
```
If you prefer to keep thumbnails, just left the list ``thumbnails_regex_list`` empty

## Contributing

Although this is a small script, pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.


## License

[MIT](LICENCE.txt)
