# Jewellery catalogue assets

The catalogue in `src/data/catalogue.ts` displays these product images, served by
Vite from `frontend/public/jewellery/`:

- gold-heart-necklace.png
- diamond-pendant-necklace.png
- pearl-earrings.png
- diamond-ring.png
- silver-bracelet.png
- classic-watch.png

When an item is selected it is fetched and sent through the normal upload
pipeline, so the backend receives the real PNG.

To add or replace an item, drop a square PNG/JPG here and update
`catalogue.ts`.
