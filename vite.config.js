import { defineConfig } from 'vite';

export default defineConfig({
  root: '.',
  publicDir: 'public',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    target: 'es2022',
    rollupOptions: {
      input: 'index.html',
      output: {
        manualChunks: {
          vendor: []  /* empty for now, add external libs later */
        }
      }
    }
  },
  server: {
    port: 3000,
    open: true
  }
});
