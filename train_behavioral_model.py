import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import time
import os

print("\n--- AEGIS AMD ROCm BEHAVIORAL ML TRAINING ENGINE ---")
print("Initializing AI parameters...")

# Attempt to use AMD ROCm/CUDA device if available, fallback to CPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
if device.type == 'cuda':
    print(f"[+] Device detected: {torch.cuda.get_device_name(0)}")
    print("[+] Using AMD ROCm/CUDA acceleration for training.")
else:
    print("[-] No compatible GPU found. Falling back to discrete CPU training.")

def generate_synthetic_data(num_samples: int = 10000):
    """
    Simulates process telemetry:
    Feature 0: CPU % usage
    Feature 1: Memory % usage
    Feature 2: Thread count
    Feature 3: Handle count
    Feature 4: IO Read velocity
    """
    # Normal behavior data
    normal_cpu = np.random.normal(2.0, 1.0, num_samples)
    normal_mem = np.random.normal(5.0, 2.0, num_samples)
    normal_threads = np.random.normal(15, 5, num_samples)
    normal_handles = np.random.normal(200, 50, num_samples)
    normal_io = np.random.normal(10, 5, num_samples)
    
    # Clip to valid numeric ranges
    data = np.column_stack([
        np.clip(normal_cpu, 0.0, 100.0),
        np.clip(normal_mem, 0.0, 100.0),
        np.clip(normal_threads, 1, 1000),
        np.clip(normal_handles, 10, 5000),
        np.clip(normal_io, 0, 10000)
    ]).astype(np.float32)
    
    # Normalize features to [0, 1] generically
    data = (data - np.min(data, axis=0)) / (np.max(data, axis=0) - np.min(data, axis=0) + 1e-6)
    return torch.tensor(data)

class ProcessBehaviorAutoencoder(nn.Module):
    def __init__(self, input_dim=5):
        super(ProcessBehaviorAutoencoder, self).__init__()
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 3) # Latent bottleneck
        )
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(3, 8),
            nn.ReLU(),
            nn.Linear(8, 16),
            nn.ReLU(),
            nn.Linear(16, input_dim),
            nn.Sigmoid() # Scale 0 to 1
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

print("\nGenerating baseline telemetry dataset...")
train_data = generate_synthetic_data(50000).to(device)

model = ProcessBehaviorAutoencoder().to(device)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.005)

EPOCHS = 10
BATCH_SIZE = 256

print("\nStarting Deep Learning Sequence...")
start_time = time.time()

for epoch in range(EPOCHS):
    permutation = torch.randperm(train_data.size()[0])
    epoch_loss = 0.0
    
    for i in range(0, train_data.size()[0], BATCH_SIZE):
        optimizer.zero_grad()
        indices = permutation[i:i+BATCH_SIZE]
        batch = train_data[indices]
        
        # Autoencoder tries to reconstruct the input
        outputs = model(batch)
        loss = criterion(outputs, batch)
        loss.backward()
        optimizer.step()
        
        epoch_loss += loss.item() * batch.size(0)
        
    epoch_loss /= train_data.size()[0]
    print(f"Epoch [{epoch+1}/{EPOCHS}], Loss: {epoch_loss:.6f}")

end_time = time.time()
print(f"\nTraining completed in {end_time - start_time:.2f} seconds.")

print("Exporting model to ONNX format for Ryzen AI NPU Inference...")

# Create dummy input for ONNX export trace
dummy_input = torch.randn(1, 5, device=device)
model.eval()

onnx_path = "aegis_behavioral_model.onnx"
torch.onnx.export(
    model, 
    dummy_input, 
    onnx_path, 
    export_params=True,
    opset_version=14,          
    do_constant_folding=True,  
    input_names=['telemetry_features'],   
    output_names=['reconstructed_features'],
    dynamic_axes={'telemetry_features' : {0 : 'batch_size'}, 'reconstructed_features' : {0 : 'batch_size'}}
)

print(f"\n[SUCCESS] AI Model exported to {onnx_path}")
print("Ready for deployment to edr_agent.py and Ryzen AI inference engine.")
