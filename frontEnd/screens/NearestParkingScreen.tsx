import React, { useState } from 'react';
import {
  View,
  Text,
  Button,
  Image,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  TouchableOpacity,
  Platform,
} from 'react-native';
import { useNearbyPhotos } from '../hooks/useNearbyPhotos';

export function NearestParkingScreen() {
  const [numCams, setNumCams] = useState(5);
  const { coords, photos, loading, error, loadPhotos } = useNearbyPhotos(numCams);

  const cameraOptions = [1, 2, 3, 4, 5, 6, 7, 8];

  // If it's the NYC boundary error, show a centered message with coordinates
  if (error?.includes(' This feature of parking spotter only works in NYC')) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorTitle}>Location Out of Range</Text>
        <Text style={styles.errorMessage}>{error}</Text>
        {coords && (
          <Text style={styles.coordsError}>
            Current Location: Lat {coords.lat.toFixed(5)}, Lng {coords.lng.toFixed(5)}
          </Text>
        )}
        <Text style={styles.helpText}>
          Use ADB commands to set NYC coordinates:{'\n'}
          adb shell settings put secure location mode 1{'\n'}
          adb emu geo fix -73.9857 40.7484
        </Text>
        <Button
          title="Try Again"
          onPress={loadPhotos}
          disabled={loading}
        />
      </View>
    );
  }

  return (
    <View style={styles.screenContainer}>
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

      <TouchableOpacity
        style={[styles.mainActionButton, loading && styles.mainActionButtonDisabled]}
        onPress={loadPhotos}
        disabled={loading}
        activeOpacity={0.8}
      >
        <View style={styles.buttonGradient}>
          <Text style={styles.mainActionButtonText}>
            {loading ? 'SEARCHING...' : 'GET NEARBY PHOTOS'}
          </Text>
          <View style={styles.buttonAccent} />
        </View>
      </TouchableOpacity>
      
      {coords && (
        <Text style={styles.coords}>
          Lat {coords.lat.toFixed(5)}, Lng {coords.lng.toFixed(5)}
        </Text>
      )}

      {loading && <ActivityIndicator style={styles.loader} size="large" />}

      {/* Show other types of errors in the normal way */}
      {error && <Text style={styles.errorText}>{error}</Text>}

      <FlatList
        data={photos}
        keyExtractor={(item) => item.address}
        contentContainerStyle={styles.list}
        renderItem={({ item }) => (
          <View style={styles.photoCard}>
            <Text style={styles.photoLabel}>{item.address.replace(/_/g, " ")}</Text>
            <Image 
              source={{ uri: item.uri }} 
              style={styles.photo} 
            />
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  screenContainer: {
    flex: 1,
    paddingTop: 20,
    alignItems: 'center',
    backgroundColor: '#0f001a',
  },
  controlsContainer: {
    width: '90%',
    marginBottom: 20,
    padding: 20,
    backgroundColor: 'rgba(42, 0, 64, 0.9)',
    borderRadius: 16,
    borderWidth: 2,
    borderColor: 'rgba(255, 140, 66, 0.3)', // Orange border accent
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
    textShadowColor: '#8B5FBF', // Purple shadow for contrast
    textShadowOffset: { width: -1, height: 2 },
    textShadowRadius: 8,
    transform: [{ skewX: '-5deg' }], // Slight slant for attitude
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
    backgroundColor: '#FF8C42', // Orange sunset
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
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#0f001a',
    padding: 20,
  },
  errorTitle: {
    color: '#ff4444',
    fontSize: 26,
    fontWeight: 'bold',
    marginBottom: 16,
    textAlign: 'center',
    textShadowColor: 'rgba(255, 68, 68, 0.3)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  errorMessage: {
    color: '#fff',
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 24,
  },
  coords: {
    marginTop: 12,
    fontSize: 14,
    color: '#FFB366',
    fontFamily: 'System',
    fontWeight: '600',
    letterSpacing: 0.8,
    textShadowColor: 'rgba(255, 140, 66, 0.4)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 3,
  },
  loader: {
    marginTop: 20,
  },
  errorText: {
    color: '#ff6b9d',
    marginTop: 20,
    fontSize: 16,
    textAlign: 'center',
  },
  list: {
    padding: 16,
  },
  photoCard: {
    marginBottom: 20,
    padding: 12,
    backgroundColor: 'rgba(42, 0, 64, 0.9)',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 140, 66, 0.4)', // Orange accent border
    elevation: 8,
    shadowColor: '#FF8C42',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  photoLabel: {
    color: '#fff',
    fontSize: 18,
    marginBottom: 12,
    textAlign: 'center',
    fontWeight: '600',
    textShadowColor: 'rgba(139, 95, 191, 0.5)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 2,
  },
  photo: {
    width: 320,
    height: 240,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(139, 95, 191, 0.2)',
  },
  coordsError: {
    color: '#ffaa00',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 16,
    textAlign: 'center',
  },
  helpText: {
    color: '#ccc',
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 24,
    fontFamily: 'monospace',
    lineHeight: 18,
  },
  mainActionButton: {
    width: '90%',
    height: 60,
    borderRadius: 8,
    backgroundColor: '#FF8C42', // Orange sunset primary
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 20,
    borderWidth: 2,
    borderColor: '#FFB366', // Lighter orange border
    elevation: 12,
    shadowColor: '#FF8C42',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.6,
    shadowRadius: 12,
    position: 'relative',
    overflow: 'hidden',
  },
  mainActionButtonDisabled: {
    backgroundColor: 'rgba(255, 140, 66, 0.4)',
    borderColor: 'rgba(255, 179, 102, 0.3)',
    shadowOpacity: 0.2,
  },
  buttonGradient: {
    width: '100%',
    height: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
    zIndex: 2,
  },
  mainActionButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '900',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace', // Monospace for that distinctive look
    letterSpacing: 3,
    textShadowColor: '#FF8C42',
    textShadowOffset: { width: 2, height: 2 },
    textShadowRadius: 6,
    textTransform: 'uppercase',
    textDecorationLine: 'underline',
    textDecorationColor: 'rgba(255, 140, 66, 0.6)',
  },
  buttonAccent: {
    position: 'absolute',
    top: -20,
    right: -20,
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'rgba(139, 95, 191, 0.3)', // Purple accent
    zIndex: 1,
  },
}); 