FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build for development
EXPOSE 3000

# Start development server
CMD ["npm", "start"]