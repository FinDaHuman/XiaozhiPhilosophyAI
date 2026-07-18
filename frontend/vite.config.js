import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    // dist/ contains files owned by another local user account that this
    // shell cannot delete; overwriting works, deleting does not. Hashed
    // asset names keep index.html pointing at the fresh build regardless.
    emptyOutDir: false,
  },
})
