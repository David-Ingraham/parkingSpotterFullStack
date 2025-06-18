import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, Image, ActivityIndicator, TouchableOpacity } from 'react-native';
import { AddressAutocomplete } from '../components/AddressAutocomplete';
import { BACKEND_URL } from '@env';

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
      const response = await fetch(`${BACKEND_URL}/search_cameras`, {
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
    <View style={styles.screenContainer}>
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
          
          <FlatList
            data={images}
            keyExtractor={(item) => item.address}
            contentContainerStyle={styles.list}
            renderItem={({ item, index }) => (
              <View style={styles.photoCard}>
                <Text style={styles.photoLabel}>
                  {index === 0 ? '📍 ' : ''}{item.address.replace(/_/g, " ")}
                </Text>
                <Image 
                  source={{ uri: item.url }} 
                  style={styles.photo} 
                />
              </View>
            )}
          />
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  screenContainer: {
    flex: 1,
    backgroundColor: '#2e003e',
  },
  searchContainer: {
    padding: 20,
  },
  title: {
    color: '#fff',
    fontSize: 24,
    marginBottom: 20,
    textAlign: 'center',
  },
  controlsContainer: {
    marginBottom: 20,
    padding: 16,
    backgroundColor: '#3f0058',
    borderRadius: 8,
  },
  selectorLabel: {
    color: '#fff',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 12,
  },
  buttonGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: 8,
  },
  cameraButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#555',
    justifyContent: 'center',
    alignItems: 'center',
    margin: 4,
  },
  cameraButtonSelected: {
    backgroundColor: '#8B5FBF',
  },
  cameraButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  cameraButtonTextSelected: {
    color: '#fff',
  },
  resultContainer: {
    flex: 1,
    padding: 20,
  },
  selectedText: {
    color: '#fff',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
  },
  loader: {
    marginTop: 20,
  },
  errorText: {
    color: '#ff4444',
    textAlign: 'center',
    marginTop: 20,
  },
  list: {
    paddingBottom: 20,
  },
  photoCard: {
    marginBottom: 16,
    padding: 8,
    backgroundColor: '#3f0058',
    borderRadius: 8,
    alignItems: 'center',
  },
  photoLabel: {
    color: '#fff',
    fontSize: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  photo: {
    width: 320,
    height: 240,
    borderRadius: 8,
  },
}); 