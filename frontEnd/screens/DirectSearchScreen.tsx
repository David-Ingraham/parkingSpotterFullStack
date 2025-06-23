import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Image, ActivityIndicator, TouchableOpacity, Platform } from 'react-native';
import { AddressAutocomplete } from '../components/AddressAutocomplete';
import { API_CONFIG } from '../config';

type CameraImage = {
  address: string;
  url: string;
};

export function DirectSearchScreen() {
  const [selectedAddress, setSelectedAddress] = useState<string | null>(null);
  const [images, setImages] = useState<CameraImage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [numCams, setNumCams] = useState(5);

  const cameraOptions = [1, 2, 3, 4, 5, 6, 7, 8];

  const handleAddressSelect = async (address: string) => {
    setSelectedAddress(address);
    setIsLoading(true);
    setError(null);
    setImages([]);

    try {
      const response = await fetch(`${API_CONFIG.baseUrl}/search_cameras`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          addresses: [address],
          numCams: numCams
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch camera images');
      }

      const data = await response.json();
      
      if (data.images && data.images.length > 0) {
        setImages(data.images);
      } else {
        setError('No images available for this area');
      }
    } catch (err) {
      setError('Failed to load camera images. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ScrollView style={styles.screenContainer} contentContainerStyle={styles.scrollContent}>
      <View style={styles.searchContainer}>
        <Text style={styles.title}>Search by Address</Text>
        
        <View style={styles.controlsContainer}>
          <Text style={styles.selectorLabel}>Number of Cameras: {numCams}</Text>
          <View style={styles.buttonGrid}>
            {cameraOptions.map((count) => (
              <TouchableOpacity
                key={count}
                style={[
                  styles.cameraButton,
                  numCams === count && styles.cameraButtonSelected
                ]}
                onPress={() => setNumCams(count)}
              >
                <Text style={[
                  styles.cameraButtonText,
                  numCams === count && styles.cameraButtonTextSelected
                ]}>
                  {count}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <AddressAutocomplete onSelectAddress={handleAddressSelect} />
      </View>
      
      {selectedAddress && (
        <View style={styles.resultContainer}>
          <Text style={styles.selectedText}>
            Nearby cameras around: {selectedAddress.replace(/_/g, ' ')}
          </Text>
          
          {isLoading && <ActivityIndicator style={styles.loader} size="large" />}
          
          {error && <Text style={styles.errorText}>{error}</Text>}
          
          {images.map((image, index) => (
            <View key={image.address} style={styles.photoCard}>
              <Text style={styles.photoLabel}>
                {index === 0 ? '📍 ' : ''}{image.address.replace(/_/g, " ")}
              </Text>
              <Image 
                source={{ uri: image.url }} 
                style={styles.photo} 
              />
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screenContainer: {
    flex: 1,
    backgroundColor: '#0f001a',
  },
  scrollContent: {
    flexGrow: 1,
  },
  searchContainer: {
    padding: 20,
    backgroundColor: 'rgba(26, 0, 43, 0.8)',
  },
  title: {
    color: '#FFB366',
    fontSize: 32,
    marginBottom: 24,
    textAlign: 'center',
    fontWeight: '900',
    fontFamily: Platform.OS === 'ios' ? 'Courier New' : 'monospace',
    textShadowColor: '#8B5FBF',
    textShadowOffset: { width: -2, height: 3 },
    textShadowRadius: 8,
    letterSpacing: 3,
    textTransform: 'uppercase',
    transform: [{ skewX: '-3deg' }],
  },
  controlsContainer: {
    marginBottom: 20,
    padding: 20,
    backgroundColor: 'rgba(42, 0, 64, 0.9)',
    borderRadius: 16,
    borderWidth: 2,
    borderColor: 'rgba(255, 140, 66, 0.3)',
    elevation: 8,
    shadowColor: '#FF8C42',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
  },
  selectorLabel: {
    color: '#FFB366',
    fontSize: 20,
    textAlign: 'center',
    marginBottom: 16,
    fontWeight: '900',
    fontFamily: Platform.OS === 'ios' ? 'Courier New' : 'monospace',
    letterSpacing: 2.5,
    textTransform: 'uppercase',
    textShadowColor: '#8B5FBF',
    textShadowOffset: { width: -1, height: 2 },
    textShadowRadius: 8,
    transform: [{ skewX: '-5deg' }],
  },
  buttonGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: 10,
  },
  cameraButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(85, 85, 85, 0.8)',
    justifyContent: 'center',
    alignItems: 'center',
    margin: 4,
    borderWidth: 1,
    borderColor: 'rgba(139, 95, 191, 0.2)',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  cameraButtonSelected: {
    backgroundColor: '#FF8C42',
    borderColor: '#FFB366',
    elevation: 8,
    shadowColor: '#FF8C42',
    shadowOpacity: 0.8,
  },
  cameraButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  cameraButtonTextSelected: {
    color: '#fff',
    textShadowColor: 'rgba(0, 0, 0, 0.3)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 2,
  },
  resultContainer: {
    flex: 1,
    padding: 20,
    backgroundColor: 'rgba(15, 0, 26, 0.9)',
  },
  selectedText: {
    color: '#FFB366',
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 20,
    fontWeight: '800',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    letterSpacing: 1.5,
    textShadowColor: '#8B5FBF',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
    textTransform: 'uppercase',
  },
  loader: {
    marginTop: 20,
  },
  errorText: {
    color: '#ff6b9d',
    textAlign: 'center',
    marginTop: 20,
    fontSize: 16,
    fontWeight: '500',
  },
  list: {
    paddingBottom: 20,
  },
  photoCard: {
    marginBottom: 20,
    padding: 12,
    backgroundColor: 'rgba(42, 0, 64, 0.9)',
    borderRadius: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 140, 66, 0.4)',
    elevation: 8,
    shadowColor: '#FF8C42',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  photoLabel: {
    color: '#FFB366',
    fontSize: 16,
    marginBottom: 12,
    textAlign: 'center',
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    letterSpacing: 1,
    textShadowColor: '#8B5FBF',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 3,
    textTransform: 'uppercase',
  },
  photo: {
    width: 320,
    height: 240,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(139, 95, 191, 0.2)',
  },
}); 