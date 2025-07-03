import React, { useState, useCallback, useRef } from 'react';
import { View, Text, StyleSheet, ScrollView, Image, ActivityIndicator, TouchableOpacity, Platform, KeyboardAvoidingView, Dimensions } from 'react-native';
import { useHeaderHeight } from '@react-navigation/elements';
import { AutocompleteDropdown, AutocompleteDropdownContextProvider, IAutocompleteDropdownRef, AutocompleteDropdownItem } from 'react-native-autocomplete-dropdown';
import { API_CONFIG } from '../config';
import cameraLocations from '../data/camera_locations.json';
import { CameraLocations } from '../types/camera';

const typedCameraLocations = cameraLocations as CameraLocations;

type CameraImage = {
  address: string;
  url: string;
};

type SuggestionItem = {
  id: string;
  title: string;
};

export function DirectSearchScreen() {
  const [selectedAddress, setSelectedAddress] = useState<string | null>(null);
  const [images, setImages] = useState<CameraImage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [numCams, setNumCams] = useState(5);
  const [suggestionsList, setSuggestionsList] = useState<SuggestionItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<SuggestionItem | null>(null);
  
  const headerHeight = useHeaderHeight();
  const dropdownController = useRef<IAutocompleteDropdownRef | null>(null);
  const cameraOptions = [1, 2, 3, 4, 5, 6, 7, 8];

  // Convert underscore format to display format
  const formatAddress = (address: string) => {
    return address.replace(/_/g, ' ').replace(/\s+/g, ' ').trim();
  };

  // Industry standard: debounced search with proper data transformation
  const getSuggestions = useCallback((query: string) => {
    if (!query || query.length < 1) {
      setSuggestionsList([]);
      return;
    }

    const searchTerm = query.toLowerCase();
    const matches = Object.keys(typedCameraLocations)
      .filter(address => 
        formatAddress(address).toLowerCase().includes(searchTerm)
      )
      .slice(0, 10) // Limit for performance
      .map(address => ({
        id: address,
        title: formatAddress(address),
      }));

    setSuggestionsList(matches);
  }, []);

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

  // Industry standard: proper item selection handling
  const handleSelectItem = (item: AutocompleteDropdownItem | null) => {
    if (item && item.id) {
      const suggestionItem = { id: item.id, title: item.title || '' };
      setSelectedItem(suggestionItem);
      handleAddressSelect(item.id);
    }
  };

  const handleSearchPress = () => {
    if (selectedItem) {
      handleAddressSelect(selectedItem.id);
    }
  };

  return (
    // Industry standard: Context provider at screen level
    <AutocompleteDropdownContextProvider>
      <KeyboardAvoidingView
        style={styles.screenContainer}
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        keyboardVerticalOffset={Platform.OS === "ios" ? 100 : 20}
      >
        <ScrollView 
          style={{ flex: 1 }} 
          contentContainerStyle={{ paddingTop: headerHeight, flexGrow: 1 }}
          keyboardShouldPersistTaps="handled"
          keyboardDismissMode="interactive"
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.searchContainer}>
            <Text style={styles.title}>Search by Address</Text>
            
            <View style={styles.controlsContainer}>
              <Text style={styles.selectorLabel}>Number of Cameras: {numCams}</Text>
              <Text style={styles.helperText}>
                📸 Choose how many camera views to show from the selected area
              </Text>
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

            {/* Help text for address search */}
            <View style={styles.helpContainer}>
              <Text style={styles.helpTitle}>💡 How to Search:</Text>
              <Text style={styles.helpText}>
                • Start typing an NYC address or intersection
              </Text>
              <Text style={styles.helpText}>
                • Select from the dropdown suggestions that appear
              </Text>
              <Text style={styles.helpText}>
                • We'll find nearby traffic cameras automatically
              </Text>
              <Text style={styles.helpText}>
                • No suggestions? Try "Broadway 42nd", "5th Ave 23rd", etc.
              </Text>
            </View>

            {/* Industry standard autocomplete implementation */}
            <View style={styles.autocompleteContainer}>
              <AutocompleteDropdown
                controller={(controller) => {
                  dropdownController.current = controller;
                }}
                clearOnFocus={false}
                closeOnBlur={true}
                closeOnSubmit={true}
                onChangeText={getSuggestions}
                onSelectItem={handleSelectItem}
                dataSet={suggestionsList}
                debounce={300}
                useFilter={false} // We handle filtering ourselves
                textInputProps={{
                  placeholder: "Start typing: Broadway, 5th Ave, etc...",
                  placeholderTextColor: "#666",
                  style: styles.searchInput,
                }}
                inputContainerStyle={styles.inputContainer}
                suggestionsListContainerStyle={styles.suggestionsContainer}
                suggestionsListTextStyle={styles.suggestionText}
                containerStyle={styles.dropdownContainer}
                renderItem={(item) => (
                  <View style={styles.suggestionItem}>
                    <Text style={styles.suggestionText}>{item.title}</Text>
                  </View>
                )}
                inputHeight={50}
                suggestionsListMaxHeight={Dimensions.get('window').height * 0.3}
                showChevron={false}
                showClear={true}
                ChevronIconComponent={undefined}
                ClearIconComponent={<Text style={styles.clearIcon}>✕</Text>}
              />
            </View>

            <TouchableOpacity
              style={[
                styles.searchButton,
                (!selectedItem || isLoading) && styles.searchButtonDisabled
              ]}
              onPress={handleSearchPress}
              disabled={!selectedItem || isLoading}
            >
              <Text style={styles.searchButtonText}>
                {!selectedItem ? "Select an address first" : isLoading ? "Searching..." : "Find Nearby Cameras"}
              </Text>
            </TouchableOpacity>
          </View>
          
          {selectedAddress && (
            <View style={styles.resultContainer}>
              <Text style={styles.selectedText}>
                📍 Showing {numCams} cameras near: {selectedAddress.replace(/_/g, ' ')}
              </Text>
              
              {isLoading && (
                <View style={styles.loadingContainer}>
                  <ActivityIndicator style={styles.loader} size="large" color="#FF8C42" />
                  <Text style={styles.loadingText}>Finding cameras and fetching live images...</Text>
                </View>
              )}
              
              {error && (
                <View style={styles.errorContainer}>
                  <Text style={styles.errorText}>{error}</Text>
                  <Text style={styles.errorHelpText}>
                    💡 Try selecting a different address from the dropdown suggestions
                  </Text>
                </View>
              )}
              
              {images.map((image, index) => (
                <View key={image.address} style={styles.photoCard}>
                  <Text style={styles.photoLabel}>
                    {index === 0 ? '📍 ' : '📸 '}Camera {index + 1}: {image.address.replace(/_/g, " ")}
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
      </KeyboardAvoidingView>
    </AutocompleteDropdownContextProvider>
  );
}

const styles = StyleSheet.create({
  screenContainer: {
    flex: 1,
    backgroundColor: '#0f001a',
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
  helperText: {
    color: '#FFB366',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 16,
    fontWeight: '500',
    fontFamily: Platform.OS === 'ios' ? 'Courier New' : 'monospace',
    letterSpacing: 2.5,
    textTransform: 'uppercase',
    textShadowColor: '#8B5FBF',
    textShadowOffset: { width: -1, height: 2 },
    textShadowRadius: 8,
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
  // Industry standard dropdown styling
  autocompleteContainer: {
    marginBottom: 10,
    zIndex: 1000,
    elevation: Platform.OS === 'android' ? 1000 : 0,
  },
  dropdownContainer: {
    flexGrow: 1,
    flexShrink: 1,
  },
  inputContainer: {
    backgroundColor: '#fff',
    borderRadius: 8,
    borderWidth: 0,
  },
  searchInput: {
    backgroundColor: '#fff',
    borderRadius: 8,
    fontSize: 16,
    color: '#000',
    paddingHorizontal: 15,
    paddingVertical: 15,
  },
  suggestionsContainer: {
    backgroundColor: '#fff',
    borderRadius: 8,
    marginTop: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  suggestionItem: {
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  suggestionText: {
    fontSize: 16,
    color: '#000',
  },
  clearIcon: {
    color: '#666',
    fontSize: 16,
    fontWeight: 'bold',
  },
  searchButton: {
    backgroundColor: '#FF8C42',
    padding: 15,
    borderRadius: 8,
    marginTop: 10,
    alignItems: 'center',
  },
  searchButtonDisabled: {
    backgroundColor: 'rgba(255, 140, 66, 0.5)',
    opacity: 0.7,
  },
  searchButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
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
  loadingContainer: {
    alignItems: 'center',
    marginTop: 20,
  },
  loadingText: {
    color: '#FFB366',
    textAlign: 'center',
    marginTop: 10,
    fontSize: 16,
    fontWeight: '500',
    fontFamily: Platform.OS === 'ios' ? 'Courier New' : 'monospace',
  },
  errorContainer: {
    alignItems: 'center',
    marginTop: 20,
  },
  errorText: {
    color: '#ff6b9d',
    textAlign: 'center',
    fontSize: 16,
    fontWeight: '500',
  },
  errorHelpText: {
    color: '#FFB366',
    textAlign: 'center',
    marginTop: 10,
    fontSize: 14,
    fontWeight: '400',
    fontFamily: Platform.OS === 'ios' ? 'Courier New' : 'monospace',
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
  helpContainer: {
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
  helpTitle: {
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
  },
  helpText: {
    color: '#FFB366',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 16,
    fontWeight: '500',
    fontFamily: Platform.OS === 'ios' ? 'Courier New' : 'monospace',
    letterSpacing: 2.5,
    textTransform: 'uppercase',
    textShadowColor: '#8B5FBF',
    textShadowOffset: { width: -1, height: 2 },
    textShadowRadius: 8,
  },
}); 